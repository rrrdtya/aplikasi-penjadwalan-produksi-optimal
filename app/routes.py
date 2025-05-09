from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import pulp
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/solve', methods=['POST'])
def solve():
    try:
        # Get data from form
        num_products = int(request.form.get('num_products', 5))
        num_machines = int(request.form.get('num_machines', 3))
        time_limit = float(request.form.get('time_limit', 10))
        
        # Get processing times
        processing_times = {}
        machine_assignments = {}
        
        for p in range(1, num_products + 1):
            for m in range(1, num_machines + 1):
                key = f'p{p}_m{m}'
                if key in request.form and request.form[key].strip():
                    time_value = float(request.form[key])
                    if time_value > 0:
                        processing_times[(p, m)] = time_value
                        # Track which products can be produced on which machines
                        if p not in machine_assignments:
                            machine_assignments[p] = []
                        machine_assignments[p].append(m)

        # Create optimization model
        model = pulp.LpProblem("Production_Scheduling", pulp.LpMinimize)
        
        # Decision variables: x[p, m] is the number of units of product p produced on machine m
        x = {}
        for p in range(1, num_products + 1):
            for m in range(1, num_machines + 1):
                if (p, m) in processing_times:
                    x[(p, m)] = pulp.LpVariable(f"x_{p}_{m}", lowBound=0, cat='Integer')
        
        # Decision variable for the maximum completion time across all machines
        max_time = pulp.LpVariable("max_time", lowBound=0)
        
        # Objective function: minimize max completion time
        model += max_time, "Minimize_Maximum_Completion_Time"
        
        # Constraints: time limit for each machine
        for m in range(1, num_machines + 1):
            model += pulp.lpSum([processing_times.get((p, m), 0) * x.get((p, m), 0) 
                               for p in range(1, num_products + 1) 
                               if (p, m) in processing_times]) <= time_limit, f"Time_Limit_Machine_{m}"
        
        # Constraints: each machine's completion time must not exceed max_time
        for m in range(1, num_machines + 1):
            model += pulp.lpSum([processing_times.get((p, m), 0) * x.get((p, m), 0) 
                               for p in range(1, num_products + 1) 
                               if (p, m) in processing_times]) <= max_time, f"Max_Time_Machine_{m}"
        
        # Constraints: produce at least one unit of each product
        for p in range(1, num_products + 1):
            if p in machine_assignments:
                model += pulp.lpSum([x.get((p, m), 0) for m in machine_assignments[p]]) >= 1, f"Min_Production_Product_{p}"
        
        # Solve the model
        model.solve(pulp.PULP_CBC_CMD(msg=False))
        
        # Format results
        status = pulp.LpStatus[model.status]
        
        if status != "Optimal":
            return render_template('index.html', error=f"No optimal solution found. Status: {status}")
        
        # Extract results
        result_data = []
        for p in range(1, num_products + 1):
            for m in range(1, num_machines + 1):
                if (p, m) in x and pulp.value(x[(p, m)]) > 0:
                    units = int(pulp.value(x[(p, m)]))
                    time_used = processing_times[(p, m)] * units
                    result_data.append({
                        'product': f'P{p}',
                        'machine': f'M{m}',
                        'units': units,
                        'processing_time': processing_times[(p, m)],
                        'total_time': time_used
                    })
        
        # Calculate time usage per machine
        machine_usage = {}
        for m in range(1, num_machines + 1):
            machine_usage[f'M{m}'] = sum(item['total_time'] for item in result_data if item['machine'] == f'M{m}')
        
        # Create visualization
        fig, ax = plt.subplots(1, 2, figsize=(12, 6))
        
        # Bar chart for machine utilization
        machines = list(machine_usage.keys())
        times = list(machine_usage.values())
        ax[0].bar(machines, times, color='skyblue')
        ax[0].axhline(y=time_limit, color='r', linestyle='-', label='Time Limit')
        ax[0].set_xlabel('Mesin')
        ax[0].set_ylabel('Waktu (jam)')
        ax[0].set_title('Penggunaan Waktu per Mesin')
        ax[0].legend()
        
        # Gantt chart-like visualization for machine allocation
        if result_data:
            machines = sorted(set(item['machine'] for item in result_data))
            products = sorted(set(item['product'] for item in result_data))
            colors = plt.cm.tab10(np.linspace(0, 1, len(products)))
            product_color = {p: colors[i] for i, p in enumerate(products)}
            
            cumulative_time = {m: 0 for m in machines}
            
            for item in sorted(result_data, key=lambda x: (x['machine'], x['product'])):
                m = item['machine']
                p = item['product']
                time = item['total_time']
                
                ax[1].barh(m, time, left=cumulative_time[m], color=product_color[p], 
                          edgecolor='white', alpha=0.8)
                
                # Add text label in the middle of the bar
                ax[1].text(cumulative_time[m] + time/2, m, f"{p}\n({item['units']})", 
                          ha='center', va='center', color='black', fontweight='bold')
                
                cumulative_time[m] += time
            
            # Add legend for products
            handles = [plt.Rectangle((0,0), 1, 1, color=product_color[p]) for p in products]
            ax[1].legend(handles, products, loc='upper right', title='Produk')
            
            ax[1].set_xlabel('Waktu (jam)')
            ax[1].set_title('Jadwal Produksi')
            ax[1].grid(axis='x', linestyle='--', alpha=0.7)
            ax[1].set_xlim(0, time_limit)
        
        plt.tight_layout()
        
        # Convert plot to base64 for embedding in HTML
        buf = io.BytesIO()
        FigureCanvas(fig).print_png(buf)
        plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close(fig)
        
        return render_template('result.html', 
                              result_data=result_data, 
                              machine_usage=machine_usage,
                              max_time=pulp.value(max_time),
                              time_limit=time_limit,
                              plot_url=plot_data)
    
    except Exception as e:
        return render_template('index.html', error=f"Error: {str(e)}")

@main.route('/example', methods=['GET'])
def example():
    # Pre-populate with example data from the problem statement
    example_data = {
        'num_products': 5,
        'num_machines': 3,
        'time_limit': 10,
        'processing_times': {
            (1, 1): 2,  # P1 on M1: 2 hours
            (2, 2): 3,  # P2 on M2: 3 hours
            (3, 1): 4,  # P3 on M1: 4 hours
            (4, 3): 1,  # P4 on M3: 1 hour
            (5, 2): 2,  # P5 on M2: 2 hours
        }
    }
    
    return render_template('example.html', data=example_data) 

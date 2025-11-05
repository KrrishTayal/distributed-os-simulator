import streamlit as st
import pandas as pd
import random
import time
from collections import deque

#  CONFIGURATION 
NUM_WORKERS = 4
WORKER_NAMES = [f"Worker {i+1}" for i in range(NUM_WORKERS)]
WORKER_COLORS = {
    "Worker 1": "#4ade80",  
    "Worker 2": "#38bdf8", 
    "Worker 3": "#fde047",  
    "Worker 4": "#f87171",
}
WORKER_MEMORY = 100  

#  1. SIMULATION CORE LOGIC 

def initialize_simulation(num_tasks, min_time, max_time, quantum):
    """Initializes the tasks, workers, and state variables."""
    # Initialize tasks with CPU + memory requirements
    tasks = []
    for i in range(1, num_tasks + 1):
        processing_time = random.randint(min_time, max_time)
        memory_required = random.randint(10, 40)  # MB
        tasks.append({
            'id': f'Task {i}',
            'initial_time': processing_time,
            'remaining_time': processing_time,
            'memory_required': memory_required,
            'arrival_time': 0,
            'start_time': None,
            'finish_time': None,
            'worker': None,
            'status': 'Pending'
        })
    
    # Initialize worker state
    workers_free_at = {name: 0 for name in WORKER_NAMES}
    workers_memory = {name: WORKER_MEMORY for name in WORKER_NAMES}
    
    st.session_state.tasks = tasks
    st.session_state.workers_free_at = workers_free_at
    st.session_state.workers_memory = workers_memory
    st.session_state.time_quantum = quantum
    st.session_state.current_time = 0
    st.session_state.history = []
    st.session_state.is_running = True
    st.session_state.task_queue = deque(tasks)
    st.session_state.running_tasks = {}

def step_simulation():
    """Executes one unit of time in the simulation."""
    if not st.session_state.is_running:
        return

    st.session_state.current_time += 1
    current_time = st.session_state.current_time
    completed_task_ids = []

    #  1. Process currently running tasks 
    for worker_name, task in list(st.session_state.running_tasks.items()):
        is_quantum_up = (current_time - task.get('quantum_start_time', current_time - st.session_state.time_quantum)) >= st.session_state.time_quantum
        task['remaining_time'] -= 1

        if task['start_time'] is None:
            task['start_time'] = current_time - 1

        if task['remaining_time'] <= 0:
            #  TASK COMPLETED 
            task['finish_time'] = current_time
            task['status'] = 'Completed'

            # Release memory
            st.session_state.workers_memory[worker_name] += task['memory_required']

            st.session_state.history.append({
                'Time': current_time,
                'Task': task['id'],
                'Worker': worker_name,
                'Action': f"COMPLETED (Used {task['memory_required']}MB)",
                'Remaining': 0
            })

            st.session_state.workers_free_at[worker_name] = current_time
            del st.session_state.running_tasks[worker_name]
            completed_task_ids.append(task['id'])

        elif is_quantum_up:
            #  TASK PREEMPTED 
            st.session_state.history.append({
                'Time': current_time,
                'Task': task['id'],
                'Worker': worker_name,
                'Action': f"PREEMPTED (Remaining {task['remaining_time']}, Holding {task['memory_required']}MB)",
                'Remaining': task['remaining_time']
            })

            # Preemption — keep memory allocated
            st.session_state.task_queue.append(task)
            st.session_state.workers_free_at[worker_name] = current_time
            del st.session_state.running_tasks[worker_name]
        else:
            task['status'] = 'Running'

    #  2. Dispatch tasks to free workers (with memory check) 
    free_workers = [w for w, free_time in st.session_state.workers_free_at.items() if free_time <= current_time]
    
    for worker_name in free_workers:
        if st.session_state.task_queue:
            next_task = st.session_state.task_queue.popleft()
            required_mem = next_task['memory_required']
            
            if st.session_state.workers_memory[worker_name] >= required_mem:
                # Allocate memory and run
                st.session_state.workers_memory[worker_name] -= required_mem
                next_task['worker'] = worker_name
                next_task['quantum_start_time'] = current_time
                next_task['status'] = 'Running'
                st.session_state.running_tasks[worker_name] = next_task

                st.session_state.history.append({
                    'Time': current_time,
                    'Task': next_task['id'],
                    'Worker': worker_name,
                    'Action': f"DISPATCHED ({required_mem}MB Allocated)",
                    'Remaining': next_task['remaining_time']
                })
            else:
                # Not enough memory → task waits
                next_task['status'] = "Waiting (No Memory)"
                st.session_state.task_queue.append(next_task)
                st.session_state.history.append({
                    'Time': current_time,
                    'Task': next_task['id'],
                    'Worker': worker_name,
                    'Action': f"WAITING - Memory full ({required_mem}MB needed)",
                    'Remaining': next_task['remaining_time']
                })

    #  3. Stop simulation if all tasks done 
    if not st.session_state.task_queue and not st.session_state.running_tasks:
        st.session_state.is_running = False
        st.session_state.history.append({
            'Time': current_time,
            'Task': 'SIMULATION',
            'Worker': 'SYSTEM',
            'Action': 'FINISHED',
            'Remaining': 0
        })

#  2. STREAMLIT UI COMPONENTS 

def display_simulation_status():
    st.subheader(f"⏱ Simulation Time: **{st.session_state.current_time}**")

    cols = st.columns(NUM_WORKERS)
    for i, worker_name in enumerate(WORKER_NAMES):
        with cols[i]:
            mem_used = WORKER_MEMORY - st.session_state.workers_memory[worker_name]
            st.metric(label=f"{worker_name} (Mem {mem_used}/{WORKER_MEMORY}MB)", 
                      value=st.session_state.running_tasks.get(worker_name, {}).get('id', 'IDLE'),
                      delta=f"Quantum {st.session_state.time_quantum}", delta_color="off")
            st.progress(mem_used / WORKER_MEMORY, text=f"{mem_used} MB used")

    st.markdown(f"**Task Queue Size:** `{len(st.session_state.task_queue)}`")

def display_results():
    completed = [t for t in st.session_state.tasks if t['status'] == 'Completed']
    if not completed:
        st.info("No tasks completed yet.")
        return

    df = pd.DataFrame(completed)
    df['TAT'] = df['finish_time'] - df['arrival_time']
    df['Wait'] = df['TAT'] - df['initial_time']
    
    st.success(" SIMULATION COMPLETE")
    st.metric("Average Turnaround Time", f"{df['TAT'].mean():.2f}")
    st.metric("Average Waiting Time", f"{df['Wait'].mean():.2f}")

    st.subheader(" Task Summary")
    st.dataframe(df[['id', 'initial_time', 'memory_required', 'start_time', 'finish_time', 'TAT', 'Wait']], hide_index=True)

    st.subheader(" Simulation Log")
    history_df = pd.DataFrame(st.session_state.history)
    st.dataframe(history_df, hide_index=True, use_container_width=True)

#  3. MAIN APP 

def main():
    st.set_page_config(page_title=" Cloud OS Scheduler Simulator", layout="wide")
    st.title(" Cloud-Based OS Simulation: CPU Scheduling + Memory Allocation")
    st.markdown("This simulator demonstrates **Round Robin scheduling** and **dynamic memory allocation** across distributed worker nodes.")

    with st.sidebar:
        st.header(" Simulation Settings")
        num_tasks = st.slider("Number of Tasks", 1, 20, 10)
        min_time = st.slider("Min CPU Time", 1, 10, 3)
        max_time = st.slider("Max CPU Time", min_time, 20, 10)
        quantum = st.slider("Round Robin Quantum", 1, 5, 2)

        if st.button(" Reset Simulation"):
            initialize_simulation(num_tasks, min_time, max_time, quantum)
            st.rerun()

        if 'is_running' not in st.session_state:
            initialize_simulation(num_tasks, min_time, max_time, quantum)

    if 'is_running' in st.session_state:
        display_simulation_status()

        total_initial = sum(t['initial_time'] for t in st.session_state.tasks)
        remaining = sum(t['remaining_time'] for t in st.session_state.task_queue) + \
                    sum(t['remaining_time'] for t in st.session_state.running_tasks.values())
        progress = (total_initial - remaining) / total_initial if total_initial > 0 else 0
        st.progress(progress, text=f"Overall Progress: {progress*100:.1f}%")

        if st.session_state.is_running:
            st.markdown("### ▶️ Simulation Controls")
            col1, col2, col3 = st.columns([1, 1, 2])
            if col1.button("Run 1 Step"):
                step_simulation()
                st.rerun()

            if st.session_state.get('auto_run', False) and col2.button("Pause"):
                st.session_state.auto_run = False
                st.rerun()
            if not st.session_state.get('auto_run', False) and col2.button("Auto Run"):
                st.session_state.auto_run = True
                st.rerun()

            speed = col3.slider("Speed (seconds per step)", 0.05, 1.0, 0.25, 0.05)

            if st.session_state.get('auto_run', False) and st.session_state.is_running:
                step_simulation()
                time.sleep(speed)
                st.rerun()

            st.markdown("")
            st.subheader("Simulation History")
            if st.session_state.history:
                hist = pd.DataFrame(st.session_state.history[-10:])
                if 'Time' in hist.columns:
                    hist = hist.sort_values(by='Time', ascending=False)
                st.dataframe(hist, hide_index=True, use_container_width=True)
            else:
                st.info("Run a step to see the simulation log.")
        else:
            display_results()

if __name__ == "__main__":
    main()

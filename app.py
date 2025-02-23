from flask import Flask, request, jsonify
from models.granite_model import chat_with_ai, call_gemini_api
app = Flask(__name__)

tasks = []  # In-memory task list (replace with database integration if needed)

@app.route('/chat', methods=['POST'])
def chat():
    """Handles AI-driven business consulting chat and task management."""
    data = request.get_json()
    print(f"Received data: {data}") 
    user_message = data.get("message")
    checklist = data.get("checklist", [])

    if not user_message:
        return jsonify({"error": "Message is required", "response": None, "updated_checklist": checklist, "tasks": tasks}), 400

    response, updated_checklist, function_call = chat_with_ai(user_message, checklist)

    result = {"response": response, "updated_checklist": updated_checklist, "tasks": tasks}

    if function_call:
        func_name = function_call.get('name')
        func_args = function_call.get('args', {})

        if func_name == 'create_task':
            result.update(create_task(func_args.get('title'), func_args.get('description')))
        elif func_name == 'update_task':
            result.update(update_task(func_args.get('task_id'), func_args.get('title'), func_args.get('description')))
        elif func_name == 'delete_task':
            result.update(delete_task(func_args.get('task_id')))

    return jsonify(result)


def create_task(title, description):
    task_id = len(tasks) + 1
    task = {'id': task_id, 'title': title, 'description': description}
    tasks.append(task)
    return {"message": "Task created successfully", "task": task, "tasks": tasks}


def update_task(task_id, title, description):
    for task in tasks:
        if task['id'] == task_id:
            task['title'] = title if title else task['title']
            task['description'] = description if description else task['description']
            return {"message": "Task updated successfully", "task": task, "tasks": tasks}
    return {"error": "Task not found", "response": None, "updated_checklist": [], "tasks": tasks}


def delete_task(task_id):
    global tasks
    tasks = [task for task in tasks if task['id'] != task_id]
    return {"message": "Task deleted successfully", "tasks": tasks}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

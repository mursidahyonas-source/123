const taskInput = document.getElementById('task-input');
const addTaskBtn = document.getElementById('add-task');
const taskList = document.getElementById('task-list');

function renderTasks(tasks = []) {
  taskList.innerHTML = '';
  tasks.forEach((task, index) => {
    const taskItem = document.createElement('li');
    if (task.completed) {
      taskItem.classList.add('completed');
    }

    const taskTextSpan = document.createElement('span');
    taskTextSpan.textContent = task.text;
    taskTextSpan.addEventListener('click', () => {
      toggleTask(index);
    });

    const deleteBtn = document.createElement('span');
    deleteBtn.textContent = 'Delete';
    deleteBtn.classList.add('delete');
    deleteBtn.addEventListener('click', (e) => {
      e.stopPropagation(); // Prevent the toggle task event from firing
      deleteTask(index);
    });

    taskItem.appendChild(taskTextSpan);
    taskItem.appendChild(deleteBtn);
    taskList.appendChild(taskItem);
  });
}

async function getTasks() {
  const result = await browser.storage.sync.get('tasks');
  return result.tasks || [];
}

async function saveTasks(tasks) {
  await browser.storage.sync.set({ tasks });
}

async function addTask() {
  const taskText = taskInput.value.trim();
  if (taskText) {
    const tasks = await getTasks();
    tasks.push({ text: taskText, completed: false });
    await saveTasks(tasks);
    renderTasks(tasks);
    taskInput.value = '';
  }
}

async function deleteTask(index) {
  const tasks = await getTasks();
  tasks.splice(index, 1);
  await saveTasks(tasks);
  renderTasks(tasks);
}

async function toggleTask(index) {
  const tasks = await getTasks();
  tasks[index].completed = !tasks[index].completed;
  await saveTasks(tasks);
  renderTasks(tasks);
}

addTaskBtn.addEventListener('click', addTask);
taskInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    addTask();
  }
});

document.addEventListener('DOMContentLoaded', async () => {
  const tasks = await getTasks();
  renderTasks(tasks);
});
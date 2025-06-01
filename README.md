# To-Do List Project

This project provides a simple and effective To-Do List application with two interfaces:

- **todo_gui.py**: A desktop GUI application built with Tkinter.
- **todo_web.py**: A web application built with Flask.

Both interfaces use the same data logic and store tasks in a shared `tasks.json` file, so you can use either interface interchangeably.

## Features

- Add, edit, delete, and mark tasks as done
- Set due date, priority, category, and notes for each task
- Archive and unarchive tasks
- Export tasks to CSV (GUI only)
- Search/filter tasks (Web only)
- View tasks in a modern, user-friendly interface

## Requirements

- Python 3.7+
- Flask (for the web app)

Install Flask if you want to use the web interface:

```
pip install flask
```

## Usage

### Desktop GUI

Run the following command to start the desktop app:

```
python todo_gui.py
```

### Web App

Run the following command to start the web app:

```
python todo_web.py
```

Then open your browser and go to [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Data Storage

All tasks are stored in `tasks.json` in the project directory. Both the GUI and web app read and write to this file.

## Notes

- You can use both interfaces at the same time; changes in one will be reflected in the other.
- The project is for educational/demo purposes and does not include user authentication or multi-user support.

## Future Improvements

- Include user authentication or multi-user support.

## License

MIT License

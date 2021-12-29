import uuid
import sys
import multiprocessing


lock = multiprocessing.Lock()

if __name__ == '__main__':
    print(sys.version)
    # Manager().dict() = is a dict that spans multiple processes it exists in shared memory
    mpd = multiprocessing.Manager().dict(
        {
            'tasks': {},
            'results': {}
        }
    )

    task_id = str(uuid.uuid4())

    tasks = mpd['tasks']

    tasks[task_id] = task_id

    mpd['tasks'] = tasks

    print(mpd)

    tasks = mpd['tasks']

    tasks.pop(task_id, None)

    mpd['tasks'] = tasks

    print(mpd)

    # when you need to mutual exclusion and you need to guarantee one process updates resources at one time.

    with lock:

        task_id = str(uuid.uuid4())

        tasks = mpd['tasks']

        tasks[task_id] = task_id

        mpd['tasks'] = tasks

    print(mpd)
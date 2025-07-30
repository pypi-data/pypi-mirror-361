# cvat_sdk_i_digit
Пакет для взаимодействия с Cvat-sdk

# Пример использования
```Python
from cvat_sdk_i_digit.cvat_api import Cvat, Settings
from cvat_sdk_i_digit.config import project_spec

cvat = Cvat(settings=Settings(host="localhost",
                              port=8080,
                              org_slug="organization_name",
                              username="admin",
                              password="admin"))

print(cvat.get_all_project())

# Ответ:
# [<Project: id=14>, <Project: id=3>]

project = cvat.create_project(project_spec)
print(project)
# Ответ:
# {'assignee': None,
#  'bug_tracker': '',
#  'created_date': datetime.datetime(2024, 5, 21, 5, 59, 25, 255094, tzinfo=tzutc()),
#  'dimension': '2d',
#  'guide_id': None,
#  'id': 14,
#  'labels': {'url': 'http://localhost:8080/api/labels?project_id=14'},
#  'name': 'example projects',
#  'organization': None,
#  'owner': {'first_name': '',
#            'id': 3,
#            'last_name': '',
#            'url': 'http://localhost:8080/api/users/3',
#            'username': 'dima'},
#  'source_storage': None,
#  'status': 'annotation',
#  'target_storage': None,
#  'task_subsets': [],
#  'tasks': {'count': 8, 'url': 'http://localhost:8080/api/tasks?project_id=14'},
#  'updated_date': datetime.datetime(2024, 5, 21, 10, 1, 16, 589005, tzinfo=tzutc()),
#  'url': 'http://localhost:8080/api/projects/14'}

print(cvat.get_task(14))
cvat.dowload_dataset(task.id, Path("/temp/dataset.zip"))

```
# Функционал
* get_all_project
* get_all_tasks
* get_all_task_from_project
* get_project
* get_task
* create_project
* create_tasks
* dowload_dataset

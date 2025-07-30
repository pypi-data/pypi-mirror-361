from cvat_sdk.core.proxies.tasks import ResourceType
from cvat_sdk import make_client
from cvat_sdk_i_digit.config import project_spec
from pathlib import Path
from pydantic import BaseModel, computed_field
from typing import Any
from cvat_sdk.core.proxies.tasks import Task
from cvat_sdk.core.proxies.projects import Project


class Settings(BaseModel):
    host: str = "localhost"
    port: int = 8080
    org_slug: str = ''

    username: str = ''
    password: str = ''

    @computed_field
    @property
    def credentials(self) -> tuple:
        return (self.username, self.password)


class Cvat:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def get_all_project(self) -> list[Project]:
        with make_client(host=self.settings.host, port=self.settings.port,
                         credentials=self.settings.credentials) as client:
            return client.projects.list()

    def get_all_tasks(self) -> list[Task]:
        with make_client(host=self.settings.host, port=self.settings.port,
                         credentials=self.settings.credentials) as client:
            return client.tasks.list()

    def get_all_task_from_project(self, id_project: int) -> list[Task]:
        with make_client(host=self.settings.host, port=self.settings.port,
                         credentials=self.settings.credentials) as client:
            tasks = client.projects.retrieve(id_project).get_tasks()
            return tasks

    def get_project(self, id_project: int) -> Project:
        with make_client(host=self.settings.host, port=self.settings.port,
                         credentials=self.settings.credentials) as client:
            return client.projects.retrieve(id_project)

    def get_task(self, id_task: int) -> Task:
        with make_client(host=self.settings.host, port=self.settings.port,
                         credentials=self.settings.credentials) as client:
            return client.tasks.retrieve(id_task)

    def create_project(self, project_spec: dict = project_spec) -> Project:
        with make_client(host=self.settings.host, port=self.settings.port,
                         credentials=self.settings.credentials) as client:
            return client.projects.create(spec=project_spec)

    def create_tasks(self, task_spec: dict, resources: Any) -> Task:
        with make_client(host=self.settings.host, port=self.settings.port,
                         credentials=self.settings.credentials) as client:
            if self.settings.org_slug != '':
                client.organization_slug = self.settings.org_slug
            return client.tasks.create_from_data(spec=task_spec, resource_type=ResourceType.LOCAL, resources=resources)

    def dowload_dataset(self, task_id: int, path_file_save: Path) -> None:
        with make_client(host=self.settings.host, port=self.settings.port,
                         credentials=self.settings.credentials) as client:
            task = client.tasks.retrieve(task_id)
            task.export_dataset(filename=path_file_save, format_name="CVAT for images 1.1", include_images=True)


if __name__ == "__main__":
    settings = Settings()
    cvat = Cvat(settings)

    # print("All projects: ")
    # print(cvat.get_all_project())

    # print("All tasks: ")
    # print(cvat.get_all_tasks())

    # print("All tasks from project: ")
    # print(cvat.get_all_task_from_project(14))

    # print("Info task: ")
    # print(cvat.get_task(12))

    print("Create project: ")
    project_spec["name"] = "Name project"
    project = cvat.create_project(project_spec)
    print(project)

    project = cvat.get_project(14)
    print(project)

    print("Create tasks: ")
    task_spec = {"name": "example projects",
                 "project_id": project.id}

    resources = [Path("/home/dima/Documents/Defects_data/temp/image0.jpeg"),
                 Path("/home/dima/Documents/Defects_data/temp/image1.jpeg")]
    task = cvat.create_tasks(task_spec, resources)
    print(task)

    print("Download dataset: ")
    cvat.dowload_dataset(task.id, Path("/home/dima/Documents/Defects_data/temp/dataset.zip"))

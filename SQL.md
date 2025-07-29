# Given tables:

* tasks (id, name, status, project_id)
* projects (id, name)

### Write the queries for:

1. get all statuses, not repeating, alphabetically ordered

    ```sql
    SELECT DISTINCT tasks.status FROM tasks
    ORDER BY tasks.status ASC;
    ```

2. get the count of all tasks in each project, order by tasks count descending

    ```sql
    SELECT tasks.project_id, COUNT(tasks.id) as task_count FROM tasks
    GROUP BY tasks.project_id;
    ```

3. get the count of all tasks in each project, order by projects names

    ```sql
    SELECT projects.name, COUNT(tasks.id) as task_count FROM projects
    LEFT JOIN tasks ON project_id = projects.id
    GROUP BY projects.name
    ORDER BY projects.name;
    ```

4. get the tasks for all projects having the name beginning with "N" letter
    
    ```sql
    SELECT * FROM tasks WHERE tasks.name LIKE 'N%';
    ```

5. get the list of al projects containing the 'a' letter in the middle of the name, and show the tasks count near each project. Mention that there can exist projects without tasks and tasks with project_id= NULL

    ```sql
    SELECT projects.id, projects.name, COUNT(tasks.id) as task_count FROM projects
    LEFT JOIN tasks ON projects.id = project_id 
    WHERE projects.name LIKE '%a% 
    GROUP BY projects.id, projects.name;
    ```

6. get the list of tasks with duplicate names. Order alphabetically

    ```sql
    SELECT tasks.id, tasks.name, tasks.status, tasks.project_id FROM tasks
    GROUP BY tasks.id, tasks.name, tasks.status, tasks.project_id
    HAVING COUNT(tasks.name) > 1
    ORDER BY tasks.name
    ```

7. get the list of tasks having several exact matches of both name and status, from the project 'Delivery’. Order by matches count

    ```sql
    SELECT tasks.name, tasks.status, COUNT(tasks.name) FROM tasks
    INNER JOIN projects ON projects.id = project_id
    WHERE projects.name = 'Delivery'
    GROUP BY tasks.name, tasks.status
    HAVING COUNT(tasks.name) > 1
    INTERSECT
    SELECT tasks.name, tasks.status, COUNT(tasks.status) FROM tasks
    INNER JOIN projects ON projects.id = project_id
    WHERE projects.name = 'Delivery'
    GROUP BY tasks.name, tasks.status
    HAVING COUNT(tasks.status) > 1
    ORDER BY count;
    ```

8. get the list of project names having more than 10 tasks in status 'completed'. Order by project_id

    ```sql
    SELECT project.name FROM project
    INNER JOIN tasks ON project.id = project_id
    WHERE tasks.status = 'completed'
    GROUP BY project.id, project.name
    HAVING COUNT(tasks.status) > 10
    ORDER BY project.id;
    ```
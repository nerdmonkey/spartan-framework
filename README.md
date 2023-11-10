# Spartan

## About Spartan
Spartan, often referred to as "The swiss army knife for serverless development," is a tool that simplifies the creation of serverless applications on popular cloud providers by generating Python code for classes and more. It streamlines your development process, saving you time and ensuring code consistency in your serverless projects.

1. Install all the required packages
```bash
pip install -r requirements.txt
```
2. Copy the .env.example to .env

3. Copy alembic.ini.example to alembic.ini

4. Create spartan.db inside the database folder

5. Create all the tables
```bash
spartan migrate upgrade
```

6. Insert dummy data
```bash
spartan db seed
```

7. Then run it using the following command
```bash
spartan serve
```

## Spartan CLI Tool
1. To install
```bash
pip install python-spartan
```

2. Try
```bash
spartan --help
```

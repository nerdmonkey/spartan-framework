# Spartan

## About Spartan
Spartan, often referred to as "The swiss army knife for serverless development," is a tool that simplifies the creation of serverless applications on popular cloud providers by generating Python code for classes and more. It streamlines your development process, saving you time and ensuring code consistency in your serverless projects.

1. Install all the required packages
```bash
pip install -r requirements.txt
```

or

```bash
poetry install
````

2. Copy the .env.example to .env

3. Then run it using the following command
```bash
uvicorn public.main:app --reload --port 8888
```
or
```bash
spartan serve
```

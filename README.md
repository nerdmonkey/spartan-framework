<p align="center"><img src="docs/ssf_banner.png" alt="Social Card of Spartan"></p>

# Spartan Serverless Framework

## About
**Spartan Serverless Framework**—"the Swiss Army knife for serverless development"—is a powerful scaffold that simplifies the creation of serverless applications on AWS. It streamlines your development process and ensures code consistency, allowing you to build scalable and efficient applications on AWS with ease.

#### Spartan Serverless Framework is versatile and can be used to efficiently develop:
- RESTful API
- Workflows or State Machines
- Small or Medium-sized ETL Pipelines
- Containerized Microservices
- Agentic AI (Coming Soon)

Fully tested in AWS, Spartan Serverless Framework is also compatible with other cloud providers like Azure and GCP, making it a flexible choice for a wide range of serverless applications.

---

## Installation & Usage

1. **Install the Spartan CLI tool:**
```bash
pip install python-spartan
```

2. **Try it out:**
```bash
spartan --help
```

3. **Set up your environment:**

<details>
<summary><strong>▶️ For Linux / macOS</strong></summary>

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

</details>

<details>
<summary><strong>🪟 For Windows PowerShell</strong></summary>

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

</details>

<details>
<summary><strong>🪟 For Windows CMD / DOS</strong></summary>

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements-dev.txt
```

</details>

4. **Copy and configure environment variables:**

```bash
cp .env.example .env  # Linux/macOS
```

```powershell
copy .env.example .env  # PowerShell
```

```cmd
copy .env.example .env  # CMD
```

5. **Run database migration:**
```bash
spartan migrate init -d sqlite
spartan migrate upgrade
```

6. **Insert seed data:**
```bash
spartan db seed
```

---

## Running the Application

### Option 1: Run directly with Python
```bash
python main.py
```

### Option 2: Run with Functions Framework
```bash
functions-framework --target=main
```

---

## Sending a Test CloudEvent

You can test the endpoint using `curl` once the app is running (default: `localhost:8080`):

```bash
curl -X POST localhost:8080 \
  -H "Content-Type: application/cloudevents+json" \
  -d '{
    "specversion" : "1.0",
    "type" : "example.com.cloud.event",
    "source" : "https://example.com/cloudevents/pull",
    "subject" : "123",
    "id" : "A234-1234-1234",
    "time" : "2018-04-05T17:31:00Z",
    "data" : "Hello Spartan Lazaro!"
}'
```

---

## Testing

Run the test suite using `pytest`:

```bash
pytest -vv
```

---

## Changelog

Please see [CHANGELOG](CHANGELOG.md) for recent updates.

---

## Contributing

Please see [CONTRIBUTING](./docs/CONTRIBUTING.md) for details on contributing.

---

## Security Vulnerabilities

Please review [our security policy](../../security/policy) for how to report vulnerabilities.

---

## Credits

- [Sydel Palinlin](https://github.com/nerdmonkey)
- [All Contributors](../../contributors)

---

## License

The MIT License (MIT). Please see the [License File](LICENSE) for more information.

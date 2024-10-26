<p align="center"><img src="./docs/logo.png" alt="Social Card of Spartan"></p>

# Spartan Framework

## About
The Spartan Framework, known as "The Swiss Army Knife for Serverless Development," is an essential tool for developers working with serverless architectures. It significantly simplifies the creation of serverless applications across major cloud providers by automatically generating Python code for classes and other necessary components. This powerful framework accelerates your development process, reduces manual coding, and ensures consistent, high-quality code in your serverless projects.

#### Spartan Framework is versatile and can be used to efficiently develop:
- API
- Workflows or State Machines
- ETL Pipelines
- Containerized Microservices

Fully tested in AWS, Spartan Framework is also compatible with other cloud providers like Azure and GCP, making it a flexible choice for a wide range of serverless applications.


## Installation
1. Install all the required packages
```bash
python -m venv .venv
pip install -r requirements.txt
```
2. Copy the .env.example to .env

3. Configure the migration
```bash
spartan migrate init -d sqlite
```

4. Create all the tables
```bash
spartan migrate upgrade
```

5. Insert dummy data
```bash
spartan db seed
```

6. Then run it using the following command
```bash
spartan serve
```

## Usage
1. To install
```bash
pip install python-spartan
```

2. Try
```bash
spartan --help
```

## Testing
```bash
pytest
```

## Changelog

Please see [CHANGELOG](CHANGELOG.md) for more information on what has changed recently.

## Contributing

Please see [CONTRIBUTING](./docs/CONTRIBUTING.md) for details.

## Security Vulnerabilities

Please review [our security policy](../../security/policy) on how to report security vulnerabilities.

## Credits

- [Sydel Palinlin](https://github.com/nerdmonkey)
- [All Contributors](../../contributors)

## License

The MIT License (MIT). Please see [License File](LICENSE) for more information.

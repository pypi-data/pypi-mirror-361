# Odoo LVE - Venezuela Location Module

A comprehensive Odoo module for Venezuela-specific location and tributary information.

## Description

This module provides Venezuela-specific data and functionality for Odoo, including:

- Tributary Units (Unidades Tributarias)
- Withholding Types (Tipos de Retención)
- Withholding Concepts (Conceptos de Retención)
- Withholding Rates (Tasas de Retención)

## Features

- **Tributary Units Management**: Complete CRUD operations for Venezuela's tributary units
- **Withholding Types**: Management of different withholding types used in Venezuela
- **Withholding Concepts**: Configuration of withholding concepts and their rates
- **Security**: Proper access control and permissions
- **Multi-language Support**: Spanish interface with English translations available

## Installation

### From PyPI

```bash
pip install odoo_lve
```

### From Source

```bash
git clone https://github.com/erpcya/odoo_lve.git
cd odoo_lve
pip install -e . --no-deps
```

**Note**: Use `--no-deps` flag because Odoo is not available on PyPI and must be installed separately.

## Usage

1. Install the module in your Odoo instance
2. Go to **Apps** and search for "Venezuela Location"
3. Install the module
4. Access the new menu items under **Venezuela** in the main menu

## Requirements

- Odoo 16.0 or later (must be installed separately)
- Python 3.8 or later

**Note**: Odoo is not available on PyPI and must be installed separately. Please refer to the [official Odoo installation guide](https://www.odoo.com/documentation/16.0/administration/install.html) for instructions.

## Development

### Setup Development Environment

```bash
git clone https://github.com/erpcya/odoo_lve.git
cd odoo_lve
pip install -e . --no-deps
pip install -r requirements-dev.txt
```

### Running Tests

```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the LGPL-3 License - see the [LICENSE](LICENSE) file for details.

## Author

- **Carlos Parada** - *Initial work* - [ERP Consultores y Asociados](https://erpya.com)

## Support

For support and questions, please contact:
- Email: cparada@erpya.com
- Website: https://erpya.com

## Changelog

### 1.0.0
- Initial release
- Tributary Units management
- Withholding Types and Concepts
- Basic security implementation

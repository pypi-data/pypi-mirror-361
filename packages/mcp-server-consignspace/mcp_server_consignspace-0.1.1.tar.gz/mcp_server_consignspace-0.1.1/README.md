# MCP Server ConsignSpace

A Model Context Protocol (MCP) server for ConsignSpace reseller API integration with Claude Desktop.

## Features

- 🛒 **Cart Management**: Add, update, remove products from cart
- 📦 **Order Processing**: Create orders, retrieve order details
- 🔍 **Product Search**: Search products with filters
- 🔐 **Secure Authentication**: Token-based API authentication
- 🔄 **Real-time Updates**: Live cart and order synchronization

## Installation

Install using pipx (recommended):

```bash
pipx install mcp-server-consignspace
```

Or using pip:

```bash
pip install mcp-server-consignspace
```

## Configuration

### 1. Get Your ConsignSpace API Token

1. Visit [ConsignSpace Token Generator](https://test.consignspace.com.au/reseller/generate_api_token.php)
2. Generate your access token
3. Copy the token for configuration

### 2. Configure Claude Desktop

Add the server to your Claude Desktop configuration file:

**Location**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

```json
{
  "mcpServers": {
    "consignspace": {
      "command": "mcp-server-consignspace",
      "env": {
        "CONSIGNSPACE_ACCESS_TOKEN": "your-token-here"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

Restart Claude Desktop to load the new server configuration.

## Available Tools

### Cart Operations
- `add-to-cart`: Add products to cart
- `get-cart`: View current cart contents
- `update-cart-quantity`: Update product quantities
- `remove-from-cart`: Remove items from cart
- `clear-cart`: Empty the cart

### Order Operations
- `create-order`: Create new order from cart
- `get-order`: Retrieve order details by ID

### Product Operations
- `get-products`: Search and browse products
- `test-auth`: Test API authentication

### Configuration
- `set-api-config`: Update API settings (optional)

## Usage Examples

### Search for Products
```
Can you search for "Charizard V (SWSH133)" products?
```

### Add to Cart
```
Add product ID 108323 to cart with quantity 2
```

### View Cart
```
Show me my current cart contents
```

### Create Order
```
Create an order with customer email "customer@example.com"
```

### Check Order Status
```
Get details for order 07-11-25-48265
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `CONSIGNSPACE_ACCESS_TOKEN` | Your ConsignSpace API token | Yes |
| `API_BASE_URL` | API base URL (optional) | No |

## Requirements

- Python 3.8+
- ConsignSpace reseller account
- Claude Desktop

## Support

- **Repository**: [GitHub Issues](https://github.com/EvanGan2023/mcp-server-consignspace/issues)
- **ConsignSpace API**: [Official Documentation](https://test.consignspace.com.au/reseller/api/)

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Changelog

### 0.1.0
- Initial release
- Cart and order management
- Product search functionality
- Authentication support
- Claude Desktop integration
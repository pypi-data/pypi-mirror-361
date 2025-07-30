import asyncio
import json
import aiohttp
import os
from typing import Dict, Any, Optional, List

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

# Configuration for the cart and orders API
API_CONFIG = {
    "base_url": os.getenv("API_BASE_URL", "https://test.consignspace.com.au/reseller/api/cart_and_orders.php"),
    "access_token": os.getenv("CONSIGNSPACE_ACCESS_TOKEN") or os.getenv("API_ACCESS_TOKEN"),  # Support both env var names for backward compatibility
}

# In-memory storage for demo purposes
cart_items: Dict[str, Any] = {}
orders: Dict[str, Any] = {}

server = Server("mcp-server-live-furloop")

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List available cart and order resources.
    """
    resources = []
    
    # Cart resources
    if cart_items:
        resources.append(
            types.Resource(
                uri=AnyUrl("cart://current"),
                name="Current Cart",
                description="Current shopping cart items",
                mimeType="application/json",
            )
        )
    
    # Order resources
    for order_id in orders:
        resources.append(
            types.Resource(
                uri=AnyUrl(f"order://internal/{order_id}"),
                name=f"Order {order_id}",
                description=f"Order details for {order_id}",
                mimeType="application/json",
            )
        )
    
    return resources

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read cart or order resource content.
    """
    if uri.scheme == "cart":
        return json.dumps(cart_items, indent=2)
    elif uri.scheme == "order":
        order_id = uri.path.lstrip("/") if uri.path else ""
        if order_id in orders:
            return json.dumps(orders[order_id], indent=2)
        else:
            raise ValueError(f"Order not found: {order_id}")
    else:
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """
    List available prompts for cart and order operations.
    """
    return [
        types.Prompt(
            name="cart-summary",
            description="Creates a summary of the current cart",
            arguments=[
                types.PromptArgument(
                    name="format",
                    description="Format of the summary (brief/detailed)",
                    required=False,
                )
            ],
        ),
        types.Prompt(
            name="order-summary",
            description="Creates a summary of an order",
            arguments=[
                types.PromptArgument(
                    name="order_id",
                    description="Order ID to summarize",
                    required=True,
                ),
                types.PromptArgument(
                    name="format",
                    description="Format of the summary (brief/detailed)",
                    required=False,
                )
            ],
        )
    ]

@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """
    Generate prompts for cart and order operations.
    """
    if name == "cart-summary":
        format_type = (arguments or {}).get("format", "brief")
        detail_prompt = " Give extensive details including pricing breakdown." if format_type == "detailed" else ""
        
        return types.GetPromptResult(
            description="Summarize the current cart",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Here is the current cart to summarize:{detail_prompt}\n\n{json.dumps(cart_items, indent=2)}",
                    ),
                )
            ],
        )
    
    elif name == "order-summary":
        order_id = (arguments or {}).get("order_id")
        if not order_id:
            raise ValueError("order_id is required for order-summary prompt")
        
        format_type = (arguments or {}).get("format", "brief")
        detail_prompt = " Give extensive details including customer info and payment method." if format_type == "detailed" else ""
        
        if order_id not in orders:
            raise ValueError(f"Order {order_id} not found")
        
        return types.GetPromptResult(
            description=f"Summarize order {order_id}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Here is order {order_id} to summarize:{detail_prompt}\n\n{json.dumps(orders[order_id], indent=2)}",
                    ),
                )
            ],
        )
    
    else:
        raise ValueError(f"Unknown prompt: {name}")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools for cart and order operations.
    """
    return [
        types.Tool(
            name="set-api-config",
            description="Set API configuration (base URL and access token)",
            inputSchema={
                "type": "object",
                "properties": {
                    "base_url": {"type": "string", "description": "API base URL"},
                    "access_token": {"type": "string", "description": "API access token"},
                },
                "required": ["base_url", "access_token"],
            },
        ),
        types.Tool(
            name="add-to-cart",
            description="Add a product to the cart",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_id": {"type": "integer", "description": "Product model ID"},
                    "quantity": {"type": "integer", "description": "Quantity to add", "default": 1},
                    "price": {"type": "number", "description": "Price per item"},
                    "selected_options": {"type": "object", "description": "Product options (color, storage, etc.)"},
                    "user_id": {"type": "string", "description": "User ID (optional)"},
                },
                "required": ["model_id", "price"],
            },
        ),
        types.Tool(
            name="get-cart",
            description="Get current cart items",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID (optional)"},
                },
            },
        ),
        types.Tool(
            name="create-order",
            description="Create an order from cart items",
            inputSchema={
                "type": "object",
                "properties": {
                    # Customer Info (Required)
                    "billing_first_name": {"type": "string", "description": "Customer first name"},
                    "billing_last_name": {"type": "string", "description": "Customer last name"},
                    "email": {"type": "string", "description": "Customer email address"},
                    "billing_phone": {"type": "string", "description": "Customer phone number with country code"},
                    "billing_phone_c_code": {"type": "string", "description": "Country code (e.g., '61' for Australia)"},
                    
                    # Payment Method (Required)
                    "payment_method": {
                        "type": "string", 
                        "enum": ["bank", "paypal", "venmo", "zelle", "amazon_gcard", "cash_app", "apple_pay", "google_pay", "coinbase", "facebook_pay", "cash", "tlc_for_kids"],
                        "description": "Payment method"
                    },
                    
                    # Payment Method Details (Conditional - based on payment_method)
                    "paypal_address": {"type": "string", "description": "PayPal email (required if payment_method=paypal)"},
                    "act_name": {"type": "string", "description": "Bank account name (required if payment_method=bank)"},
                    "act_number": {"type": "string", "description": "Bank account number (required if payment_method=bank)"},
                    "act_short_code": {"type": "string", "description": "Bank short code (required if payment_method=bank)"},
                    "venmo_address": {"type": "string", "description": "Venmo username (required if payment_method=venmo)"},
                    "zelle_address": {"type": "string", "description": "Zelle email/phone (required if payment_method=zelle)"},
                    "amazon_gcard_address": {"type": "string", "description": "Amazon gift card email (required if payment_method=amazon_gcard)"},
                    "cash_app_address": {"type": "string", "description": "Cash App username (required if payment_method=cash_app)"},
                    "apple_pay_address": {"type": "string", "description": "Apple Pay email (required if payment_method=apple_pay)"},
                    "google_pay_address": {"type": "string", "description": "Google Pay email (required if payment_method=google_pay)"},
                    "coinbase_address": {"type": "string", "description": "Coinbase wallet address (required if payment_method=coinbase)"},
                    "facebook_pay_address": {"type": "string", "description": "Facebook Pay email (required if payment_method=facebook_pay)"},
                    "cash_name": {"type": "string", "description": "Cash payment name (required if payment_method=cash)"},
                    "f_cash_phone": {"type": "string", "description": "Cash payment phone (required if payment_method=cash)"},
                    
                    # Address Info (Required)
                    "billing_address": {"type": "string", "description": "Street address"},
                    "billing_city": {"type": "string", "description": "City"},
                    "billing_state": {"type": "string", "description": "State/Province"},
                    "billing_postcode": {"type": "string", "description": "Postal/ZIP code"},
                    "billing_country": {"type": "string", "description": "Country code (e.g., 'AU')"},
                    
                    # Optional Fields
                    "billing_company_name": {"type": "string", "description": "Company name (optional)"},
                    "billing_address2": {"type": "string", "description": "Address line 2 (optional)"},
                    "sales_pack": {
                        "type": "string",
                        "enum": ["post_me_a_prepaid_label", "i_will_drop_off", "pickup"],
                        "description": "Shipping method (optional, defaults to post_me_a_prepaid_label)"
                    },
                    "note": {"type": "string", "description": "Order notes (optional)"},
                    "user_id": {"type": "string", "description": "User session ID (optional)"}
                },
                "required": [
                    "billing_first_name", 
                    "billing_last_name", 
                    "email", 
                    "billing_phone", 
                    "billing_phone_c_code",
                    "payment_method",
                    "billing_address",
                    "billing_city", 
                    "billing_state", 
                    "billing_postcode", 
                    "billing_country"
                ]
            }
        ),
        types.Tool(
            name="update-cart-quantity",
            description="Update quantity of a cart item",
            inputSchema={
                "type": "object",
                "properties": {
                    "cart_item_id": {"type": "integer", "description": "Cart item ID"},
                    "quantity": {"type": "integer", "description": "New quantity"},
                    "user_id": {"type": "string", "description": "User ID (optional)"},
                },
                "required": ["cart_item_id", "quantity"],
            },
        ),
        types.Tool(
            name="remove-from-cart",
            description="Remove an item from the cart",
            inputSchema={
                "type": "object",
                "properties": {
                    "cart_item_id": {"type": "integer", "description": "Cart item ID"},
                    "user_id": {"type": "string", "description": "User ID (optional)"},
                },
                "required": ["cart_item_id"],
            },
        ),
        types.Tool(
            name="clear-cart",
            description="Clear all items from the cart",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID (optional)"},
                },
            },
        ),
        types.Tool(
            name="get-products",
            description="Get available products and categories with optional search",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {"type": "string", "description": "Search term to filter products (e.g., 'Charizard V (SWSH133)')"},
                    "category": {"type": "string", "description": "Filter by category (optional)"},
                    "limit": {"type": "integer", "description": "Maximum number of products to return (optional)"},
                },
            },
        ),
        types.Tool(
            name="get-order",
            description="Get order details by order ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "Order ID"},
                },
                "required": ["order_id"],
            },
        ),
        types.Tool(
            name="test-auth",
            description="Test API authentication and token validity",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]

async def make_api_request(action: str, data: dict = None, method: str = "POST") -> dict:
    """Make API request to the cart and orders API."""
    if not API_CONFIG["access_token"]:
        raise ValueError("API access token not set. Use set-api-config tool first.")
    
    # Build URL with parameters in the correct order: action first, then data params, then access_token last
    url = f"{API_CONFIG['base_url']}?action={action}"
    headers = {
        "User-Agent": "curl/8.4.0",
        "Accept": "*/*"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            if method == "GET":
                if data:
                    # Add data as query parameters for GET requests
                    params = "&".join([f"{k}={v}" for k, v in data.items()])
                    url += f"&{params}"
                
                # Add access_token at the end (API is sensitive to parameter order)
                url += f"&access_token={API_CONFIG['access_token']}"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 401:
                        return {"success": False, "error": "Authentication failed: Access token is invalid or expired. Please generate a new token at https://test.consignspace.com.au/reseller/generate_api_token.php"}
                    elif response.status == 403:
                        return {"success": False, "error": "Access forbidden: Your token may not have permission for this operation"}
                    elif response.status >= 400:
                        return {"success": False, "error": f"API request failed with status {response.status}"}
                    
                    result = await response.json()
            else:
                # For POST/PUT/DELETE, add access_token to URL and send data in body
                url += f"&access_token={API_CONFIG['access_token']}"
                
                async with session.request(method, url, headers=headers, json=data or {}) as response:
                    if response.status == 401:
                        return {"success": False, "error": "Authentication failed: Access token is invalid or expired. Please generate a new token at https://test.consignspace.com.au/reseller/generate_api_token.php"}
                    elif response.status == 403:
                        return {"success": False, "error": "Access forbidden: Your token may not have permission for this operation"}
                    elif response.status >= 400:
                        return {"success": False, "error": f"API request failed with status {response.status}"}
                    
                    result = await response.json()
            
            return result
    except Exception as e:
        return {"success": False, "error": f"API request failed: {str(e)}"}

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests for cart and order operations.
    """
    if not arguments:
        arguments = {}
    
    try:
        if name == "set-api-config":
            API_CONFIG["base_url"] = arguments["base_url"]
            API_CONFIG["access_token"] = arguments["access_token"]
            
            return [
                types.TextContent(
                    type="text",
                    text=f"API configuration updated:\nBase URL: {API_CONFIG['base_url']}\nAccess Token: {'*' * 10}...{API_CONFIG['access_token'][-4:] if len(API_CONFIG['access_token']) > 4 else 'Set'}",
                )
            ]
        
        elif name == "add-to-cart":
            result = await make_api_request("add_to_cart", arguments, "POST")
            
            # Update local cart for resource listing
            if result.get("success"):
                cart_items[f"item_{len(cart_items) + 1}"] = arguments
                await server.request_context.session.send_resource_list_changed()
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Add to cart result: {json.dumps(result, indent=2)}",
                )
            ]
        
        elif name == "get-cart":
            result = await make_api_request("get_cart", arguments, "GET")
            
            # Update local cart for resource listing
            if result.get("success") and result.get("cart_items"):
                cart_items.clear()
                for i, item in enumerate(result["cart_items"]):
                    cart_items[f"item_{i + 1}"] = item
                await server.request_context.session.send_resource_list_changed()
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Cart contents: {json.dumps(result, indent=2)}",
                )
            ]
        
        elif name == "create-order":
            result = await make_api_request("create_order", arguments, "POST")
            
            # Update local orders for resource listing
            if result.get("success") and result.get("order_id"):
                orders[result["order_id"]] = result
                cart_items.clear()  # Clear cart after successful order
                await server.request_context.session.send_resource_list_changed()
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Order creation result: {json.dumps(result, indent=2)}",
                )
            ]
        
        elif name == "update-cart-quantity":
            result = await make_api_request("update_quantity", arguments, "PUT")
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Update quantity result: {json.dumps(result, indent=2)}",
                )
            ]
        
        elif name == "remove-from-cart":
            result = await make_api_request("remove_from_cart", arguments, "DELETE")
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Remove from cart result: {json.dumps(result, indent=2)}",
                )
            ]
        
        elif name == "clear-cart":
            result = await make_api_request("clear_cart", arguments, "DELETE")
            
            # Clear local cart
            cart_items.clear()
            await server.request_context.session.send_resource_list_changed()
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Clear cart result: {json.dumps(result, indent=2)}",
                )
            ]
        
        elif name == "get-products":
            result = await make_api_request("get_products", arguments, "GET")
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Available products: {json.dumps(result, indent=2)}",
                )
            ]
        
        elif name == "get-order":
            result = await make_api_request("get_order", arguments, "GET")
            
            # Update local orders for resource listing
            if result.get("success") and arguments.get("order_id"):
                orders[arguments["order_id"]] = result
                await server.request_context.session.send_resource_list_changed()
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Order details: {json.dumps(result, indent=2)}",
                )
            ]
        
        elif name == "test-auth":
            result = await make_api_request("get_products", {}, "GET")
            
            if result.get("success"):
                message = "✅ Authentication successful! Your API token is valid."
            else:
                message = f"❌ Authentication failed: {result.get('error', 'Unknown error')}"
            
            return [
                types.TextContent(
                    type="text",
                    text=message,
                )
            ]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error executing {name}: {str(e)}",
            )
        ]

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-server-live-furloop",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
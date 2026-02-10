# 🍵 Coffee Ordering Agent (Agent Chat Protocol)

A simple agent that understands natural language via the Agent Chat Protocol, lets you browse a menu, add items to your cart, and checkout—all through conversational chat. Powered by a Square-backed catalog and built for the Fetch.ai ecosystem.

---

## ✅ What this Agent Can Do

- **Natural language ordering**
  - "Show me the menu"
  - "I'll have a Cardinal Chai and a Tira-Miss-U"
  - "What's in my cart?"

- **Flexible item input**
  - Use item names from the menu
  - Say things like "add a coffee" or "I want two Karl the Fogs"
  - Works with variations (e.g., size, flavor) when available

- **Full ordering flow**
  - View the menu and prices
  - Add multiple items to your cart
  - Review your order before checkout
  - Confirm or cancel at any time

- **Clear, formatted replies**
  - Numbered menu with item names and prices
  - Cart summary with line items and total
  - Order confirmation with order ID

- **Robust handling**
  - Acknowledges receipt of messages
  - Suggests "menu" or "help" when it doesn't understand
  - Reminds you about items in your cart if you browse away

---

## ❌ What this Agent Will Not Do

- Process payment (orders are event-covered / complimentary)
- Modify an order after it's been confirmed
- Handle special dietary requests or customizations beyond the catalog
- Support multiple locations or delivery scheduling
- Answer non-ordering questions (e.g., weather, general trivia)
- Multi-language replies (English only)

---

## 🗣️ Example Prompts

| Prompt                        | Why it works                 |
| ----------------------------- | ---------------------------- |
| "What's on the menu?"         | Clear request to see options |
| "I'll have a Pep-in-yo-step"  | Natural way to add an item   |
| "Add two Love You So Matcha"  | Quantity + item name         |
| "Show my cart"                | View current order           |
| "That's all, checkout please" | Confirm and place order      |
| "Cancel"                      | Clear cart and start over    |
| "Help"                        | See available commands       |

---

## ℹ️ Tips for Best Results

- Use item names from the menu for best matching (e.g., "Cardinal Chai" instead of "chai tea")
- Add one or a few items per message; the agent understands quantities ("two coffees")
- Say "menu" first if you're not sure what's available
- Use "confirm" or "checkout" when you're ready to place your order
- Your cart is saved per chat session—you can browse the menu and come back to it

---

## 🎯 Typical Response Format

**Menu:**

```
1. Item Name - Variation (price)
2. ...
```

**Cart:**

```
Your current order:
  1. Item Name - $X.XX
  2. ...

Total: $X.XX
Say 'confirm' to checkout or 'cancel' to clear your cart.
```

**Order confirmed:**

```
Order confirmed! You ordered X item(s) for $X.XX.
Order ID: abc123...
Thank you for your order!
```

---

## 🤝 Use via ASI:One

You can invoke this agent in ASI:One by mentioning it in your prompt:

```
@<agent_address> show me the menu
```

Or:

```
@<agent_address> I'll have a Cardinal Chai and a Tira-Miss-U
```

_(Replace `<agent_address>` with this agent's address. You can find it when the agent starts or in the agent manifest.)_

---

## 🔌 How It Works (High-level)

1. Receives a chat message via the Agent Chat Protocol and acknowledges it
2. Understands what you want (menu, add item, cart, confirm, cancel, help)
3. Fetches the catalog from Square and matches your words to menu items
4. Keeps your cart in memory for your chat session
5. When you confirm, places the order with Square and replies with a confirmation
6. Sends a clear, human-friendly reply back to you

# Inventory Policy

## Stock Reservation
*   Inventory is **checked** at Cart Add.
*   Inventory is **reserved** at Checkout Start (temporary hold 15 mins).
*   Inventory is **committed** at Payment Success.

## Display
*   If stock > 5: Show "In Stock".
*   If stock <= 5: Show "Only X left!".
*   If stock == 0: Show "Sold Out".

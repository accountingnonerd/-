# Support posts for Agent 4

Short posts between releases, per GROWTH.md: no link in the post, a number in the hook, the same
follow line at the end. Each is a separate Typefully post and uses one of the month's remaining
posts.

## Post A: Thursday, November 19, 10:00 am Eastern (text only)

My own tool counted a $50 gift card as $100 of income.

Before I release a tool, a separate AI reviewer goes through it as a skeptical CPA. This week it
found 16 problems in Agent 4, the 1099-K reconciliation. The worst was this one.

A café sells a $50 gift card, paid by Visa. That $50 is on the 1099-K and in gross receipts.
Later a customer pays for lunch with the gift card. My tool added that $50 again, as a sale not on
the 1099-K. Same money, counted twice.

The fix is one line. Finding it took a reviewer who assumed the tool was wrong.

Three more it caught:
→ Sales tax taken out of gross receipts by default. Wrong in California, and in every state that taxes the seller.
→ PayPal payments marked "Refunded" dropped out of gross. PayPal re-labels them; they were still paid.
→ The year-end entry ignored money still sitting at the processor.

All fixed before release, and every one is now a test case, so it cannot come back.

What is the error you check for first when a client's 1099-K lands?

Follow for Agent 5: fixed assets.

#Accounting #Tax #CPA

## Post B: Tuesday, November 24, 10:00 am Eastern (one image: carousel slide 04)

Three things in box 1a of a 1099-K that are not what they look like:

1. Cash sales are income, and never on it.
2. Payments with the business's own gift cards are left off, and should stay off: the gift card was income when it was sold.
3. Sales tax and tips are inside it. Whether they belong on line 1 depends on the state and on who keeps the tips.

The 2026 forms arrive by January 31. The free tool that does this bridge from a Square, Stripe or
PayPal export is in my last post.

Follow for Agent 5: fixed assets.

#Accounting #Tax #SmallBusiness

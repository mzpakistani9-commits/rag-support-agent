SAMPLE_DOCS = {
    "shipping_policy": """Shipping Policy
Domestic orders ship within 24 hours of purchase using tracked courier service.
Standard delivery takes 3 to 5 business days. Express delivery is available for
an additional fee and arrives in 1 to 2 business days. Orders over Rs. 5,000
ship free. International shipping is available to 40+ countries and takes 7 to
14 business days. Customers receive a tracking number by email as soon as the
order leaves our warehouse. We do not ship on Sundays and public holidays.""",

    "refund_policy": """Refund Policy
You may request a refund within 14 days of receiving your order. Items must be
unused and in their original packaging. Refunds are processed to the original
payment method within 3 to 5 business days after the returned item is received
and inspected. Digital products and personalized items are non-refundable.
If you received a damaged or incorrect item, we replace it at no cost within
30 days — simply email support@example.com with a photo of the item.""",

    "account_password": """Account & Password
Create an account with your email address and a password of at least 8
characters, including one number and one capital letter. If you forget your
password, use the 'Forgot password' link on the login page — a reset link is
sent to your email and expires after 30 minutes. For security, enable
two-factor authentication from your Account Settings. Do not share your
password with anyone; our staff will never ask for it.""",

    "billing_and_invoices": """Billing and Invoices
Invoices are generated automatically after every successful payment and
emailed to the account holder within minutes. You can also download any
invoice from the Billing section of your account. If your bank card expires
mid-subscription, the next billing attempt is retried automatically after 3
days. Late subscriptions are paused, not cancelled, and resume once the
payment succeeds. To change your payment method, go to Account Settings >
Billing.""",

    "api_rate_limits": """API Rate Limits
The public API allows 60 requests per minute per API key on the Standard
plan, and 600 requests per minute on the Business plan. Rate limit headers
X-RateLimit-Limit and X-RateLimit-Remaining are returned on every response.
When you exceed the limit, the API returns HTTP 429 with a Retry-After
header indicating how many seconds to wait. All API calls require an
Authorization header with a Bearer token issued from the Developer portal.""",

    "integration_webhooks": """Integrations and Webhooks
Webhooks notify your systems in real time when events occur. Subscribe to
events such as order.created, order.shipped, payment.failed and ticket.created
from the Developer portal. Each webhook posts a signed JSON payload to your
endpoint URL; verify the X-Signature header with your webhook secret. Failed
deliveries are retried up to 5 times with exponential backoff. A Webhook
delivery log is available for the last 14 days.""",

    "support_hours": """Support Hours and Contact
Our support team is available Monday to Friday, 9:00 AM to 6:00 PM PKT.
Urgent issues outside these hours can be reported through the in-app chat and
are triaged within 2 hours. Contact us by email at support@example.com or by
phone at +92 300 1234567. Enterprise customers get a dedicated account manager
and 24/7 priority support.""",

    "subscription_plans": """Subscription Plans
We offer three plans. Free plan: up to 10 automated workflows and 1,000
API calls per month. Professional plan costs Rs 12,000/month and includes
unlimited workflows, 60,000 API calls, email and Slack notifications, and
priority email support. Business plan costs Rs 45,000/month and adds webhooks,
unlimited team seats, SSO, and a dedicated account manager. All paid plans can
be cancelled anytime; you keep access until the end of the billing period.""",
}
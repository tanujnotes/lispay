Source code of Lisplay.com with complete git commit history
-----------------------------------------------------------

TECH STACK: Python, Django, Postgres, hosted on AWS. Payment Gateway: Razorpay

What is Lisplay?

Lisplay allows independent artists to run their membership program which their fans could join by paying a small monthly fees. Fans could support their favourite creators financially and get some rewards in return. Similar to Patreon.com

Code Structure:

This webapp has three main django apps named -

regapp: has everything related to authentication, profile creation and other static pages like home, about etc.

dash: this is dashboard app. This is where creators see all the people who are paying them monthly. Shows all the relevant e.g. date of subscription, amount, cancelled subscriptions, monthly revenue etc.

drfapp: rest apis for mobile app using django-rest-framework.

P.S. This is my first production level Django project built from scratch about 2 years ago so the code might stink a little bit. Stay safe.

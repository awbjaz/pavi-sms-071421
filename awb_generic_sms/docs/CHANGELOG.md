# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [13.0.1.0.0-beta] - 2021-05-17
   - SMS Activity Logs
   - Full Modular Server Actions
   - Full Modular Scheduled Actions
   - ATM Ref Improvements
   - SMS Message Template Improvements
   - Improvements
   - Fixes

### Related User Stories
   - User Story #87 - As a System, canned Text Blast for Payment Reminders must be sent to Subscribers 3 days before Bill’s due date
   - User Story #93 - As a System, canned Text Blast for Disconnection Notice must be sent to Subscribers 3 Days after Due Date
   - User Story #105 - As a System, should be able to validate the current valid Template Names for SMS Sending
   - User Story #115 - As a SMS Sender, I should be able to see if the SMS has been successfully sent for On Demand SMS in Invoice
   - User Story #116 - As a SMS Sender, I should be able to see if the SMS has been successfully sent for Scheduled SMS in Invoice
   - User Story #117 - As a SMS Sender, I should be able to see if the SMS has been successfully sent for On Demand SMS in Payments
   - User Story #118 - As a SMS Sender, I should be able to see if the SMS has been successfully sent for Scheduled SMS in Payments
   - User Story #119 - As an SMS Sender, I should be able to see the message type and record linked to the SMS History
   - User Story #121 - As a system, I should be able to TEXT SOA upon Posting for the designated Billing period cutoffs of the accounts
   - User Story #122 - As a System, canned Text Blast must be sent to Subscribers 1 Day after Payment
   - User Story #124 - As an Administrator, I should be able to have access to the SMS Settings
   - User Story #126 - Send Text Message when a subscription is Permanently Disconnected (Physical Disconnection)
   - User Story #127 - Send Text Message when a subscription is Suspended (due to Non Payment)
   - User Story #131 - As an Account Officer, I should be able to send SMS (remove SMS Writer Permissions on Templates)
   - User Story #132 - As an Account Officer Central, I should be able to send SMS and update SMS Templates
   - User Story #139 - As a User, I should be warned if I access any SMS related menu or actions when I do not have any permission for Text Messaging
   - User Story #141 - As a PAVI System User, I should not be able to see the SMS Server Actions when I do not have the the correct permissions
   - User Story #142 - Text SOA Template, display of ATM Ref No should not include the first 2 digits
   - User Story #143 - Payment Reminder Template, display of ATM Ref No. should not include the first 2 digits
   - User Story #148 - Flag to Manually Skip SMS Sending for Selected Invoices
   - User Story #160 - As an Adminstrator, I should be able to assign Account Officer or Account Officer Central Role (Update the Access Rights Configurations to implement Inheritance)

### Related Technical Stories
   - #90 - Scheduled Action Special Conditions [PRODUCTION]
   - #111 - Payment Reminder "Run Manually" displays error
   - #112 - Billing Period returns "False"
   - #144 - Automated TEXT SOA Error in Scheduled Actions Settings
   - #146 - Record Limit Params for Automated SMS
   - #149 - Scheduled Action | Temporary Disconnection
   - #150 - Scheduled Action | Permanent Discon
   - #177 - Additional Condition to Process Invoices with Subscription Only

## [13.0.1.0.0-beta] - 2021-04-20
   - SMS Templates Initialization [TextSOA, Payment Reminder, Payment Notif, Disconnection, Actual Disconnection]
   - SMART API URL invalid URL catcher
   - SMS History enhancements
   - Scheduled action updates

### Related User Stories
   - User Story #59 - Payment Reminder
   - User Story #60 - Payment Notification Notice
   - User Story #61 - SMS: Name field value should be Receipients Name
   - User Story #62 - SMS: Smart API URL should have validation if the url is correct
   - User Story #73 - Remove Invoice Month in TEXT SOA, replace with Billing Period
   - User Story #74 - Change the Trigger Template for Billing Reminder to Payment Reminder from TEXT SOA
   - User Story #75 - As a system, I should be able to TEXT SOA upon Posting for the designated Billing period cutoffs of the accounts

## [13.0.1.0.0-beta] - 2021-04-14
   - Configurable SMS Gateway API URL and Token
   - Security Access Rights, Roles, Groups ( Administrator, Account Officer )
   - SMS Template Fixes, Updates and remove Placeholders
   - Validations

### Related User Stories
   - User Story #47 - As a System Admin, I should be able to turn on/off the SMS Gateway Feature
   - User Story #48 - As a System Admin, I should be able to configure the Smart API URL Instance and Authentication Token
   - User Story #49 - As a System Admin, I should be able to give a User permission to access to the SMS Gateway Feature
   - User Story #50 - As a System Admin, I should be able to view the SMS History
   - User Story #51 - Missing Peso and Comma sign in Amounts
   - User Story #52 - Message Text Area should be empty when creating new Template
   - User Story #53 - SMS for Draft Invoice has "Sent" status
   - User Story #54 - Validations: SMS Template, SMS Settings, Actions
   - User Story #57 - Month of Billing : Based on Posting Date > New Month Field for Invoice


## [13.0.1.0.0-beta] - 2021-04-08
   - Configure SMS Templates ( PAVI Requirements )
   - On-demand SMS
   - Schedule SMS
   - SMS History

### Related User Stories
   - User Story #19 - As an Account Officer, I should be able to create and setup an SMS Template for Customer Billing Reminder
   - User Story #23 - As an Account Officer, I should be able to create and setup an SMS Template for the Disconnection Notice Reminder
   - User Story #24 - As an Account Officer, I should be able to create and setup an SMS Template for the Actual Disconnection Notice
   - User Story #20 - As an Account Officer, I should be able to Send On-Demand SMS for Customer Billing Reminder
   - User Story #27 - As an Account Officer, I should be able to Send On-Demand SMS for Disconnection Notice Reminder
   - User Story #28 - As an Account Officer, I should be able to Send On-Demand SMS for Actual Disconnection Reminder
   - User Story #22 - As a System, canned Text Blast must be sent to Subscribers 3 days before Bill’s due date
   - User Story #26 - As a System, canned Text Blast must be sent to Subscribers 3 days after Due Date – sending of Disconnection Notice
   - User Story #25 - As a System, canned Text Blast must be sent to Subscribers 7 days after Due Date – Actual System Disconnection
   - User Story #46 - As an Account Officer, I should be able to Send On-Demand SMS for Generic Advisories
   - User Story #47 - As a System Admin, I should be able to turn on/off the SMS Gateway Feature

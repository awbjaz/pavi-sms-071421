# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

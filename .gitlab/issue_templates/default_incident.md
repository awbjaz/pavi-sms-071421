# Definition of Ready

**FC/QA Checklist**
- [ ] Incident Summary
- [ ] Test Data
- [ ] Screenshots
- [ ] Steps to Replicate
- [ ] Actual & Expected Result
- [ ] Tag Severity : Critical , Major , Minor
- [ ] Tag Incident Type : SIT Incident, SAT Incident, UAT Incident, PROD Incident
- [ ] Tag Environment
- [ ] Tag RCA for Client Reported incidents prior handover to DEV
- [ ] Add Version (Build No. / Release No.)

## Depends On
- Ticket No. : Description
- Other Dependencies

## Related To
- User Story No.: Description

# Definition of Done

## INCIDENT DESCRIPTION

**Summary**

(Summarize the bug encountered concisely)

**Steps to Replicate**

(How one can reproduce the issue - this is very important)

**Actual Result**

(What actually happens)

**Expected Result**

(What you should see instead)


## RESOLUTION

**Possible fixes**

(If you can, link to the line of code that might be responsible for the problem)

**DEV/FC Tasks**
- [ ] Tag RCA
- [ ] Fix
- [ ] Deploy

**QA Tasks**
- [ ] Fix Validation
- [ ] Release Notes

/label ~bug ~reproduced ~needs-investigation
/cc @project-manager
/assign @qa-tester



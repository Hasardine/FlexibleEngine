# How To Start and Stop RDS Instances 

Using FGS (FunctionGraph Servcie), we can automate Relationals Database to start and stop automatically

FGS provide multiples triggers :
- APIG (API Gateway)
- CTS (Cloud Trace Service)
- DIS (Data Ingestion Service)
- OBS (Object Storage Service)
- SMN (Simple Message Notifictaion)
- Timer

For this demo, you need to create 2 FGS functions using 2 Timer triger and the 2 script provided
- Start 1 RDS Instance every working day at 8:30 using cron expression: `0 30 8 ? * Mon-Fri`
- Stop 1 RDS instance evry working day at 18:30 using cron expression: `0 30 18 ? * Mon-Fri`



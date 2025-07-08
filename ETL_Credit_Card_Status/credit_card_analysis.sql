 # 1. Total Income by Gender
SELECT 
    Applicant_Gender, 
    SUM(Total_Income) AS Total_Income
FROM credit_card_approval_status.applicant_details
GROUP BY Applicant_Gender;

# 2. Count of Applicants by Job Title

SELECT 
    Job_Title, 
    COUNT(*) AS Applicant_Count
FROM credit_card_approval_status.applicant_details
GROUP BY Job_Title
ORDER BY Applicant_Count DESC;

# 3. Approval Status based on Employement status

SELECT 
    Job_Title,
    COUNT(*) AS Total_Applicants,
    SUM(CASE WHEN Status = 1 THEN 1 ELSE 0 END) AS Approved,
    ROUND((SUM(CASE WHEN Status = 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(*)) * 100, 2) AS Approval_Rate
FROM 
    applicant_details
GROUP BY 
    Job_Title;


# 4. Approval Rate by Gender
SELECT 
    Applicant_Gender, 
    AVG(Status)*100 AS Approval_Rate
FROM credit_card_approval_status.applicant_details
GROUP BY Applicant_Gender;

# 5. Approval Rate by Applicant Demographics
SELECT 
    Applicant_Gender,
    Family_Status,
    COUNT(*) AS Total_Applicants,
    SUM(CASE WHEN Status = 1 THEN 1 ELSE 0 END) AS Approved,
    ROUND((SUM(CASE WHEN Status = 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(*)) * 100, 2) AS Approval_Rate
FROM 
    credit_card_approval_status.applicant_details
GROUP BY 
    Applicant_Gender, Family_Status;
    
# 6. Approval Rate by Education Level

SELECT 
    Education_Type,
    COUNT(*) AS Total_Applicants,
    SUM(CASE WHEN Status = 1 THEN 1 ELSE 0 END) AS Approved,
    ROUND((SUM(CASE WHEN Status = 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(*)) * 100, 2) AS Approval_Rate
FROM 
    credit_card_approval_status.applicant_details
GROUP BY 
    Education_Type;

# 7. Impact of Family Size on Approval
SELECT 
    Total_Family_Members,
    COUNT(*) AS Total_Applicants,
    SUM(CASE WHEN Status = 1 THEN 1 ELSE 0 END) AS Approved,
    ROUND((SUM(CASE WHEN Status = 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(*)) * 100, 2) AS Approval_Rate
FROM 
    credit_card_approval_status.applicant_details
GROUP BY 
    Total_Family_Members;

# 8. Approval type by housing_type

SELECT 
    Housing_Type,
    COUNT(*) AS Total_Applicants,
    SUM(CASE WHEN Status = 1 THEN 1 ELSE 0 END) AS Approved,
    ROUND((SUM(CASE WHEN Status = 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(*)) * 100, 2) AS Approval_Rate
FROM 
    credit_card_approval_status.applicant_details
GROUP BY 
    Housing_Type;
    
# 9. Age and Experience Impact on Approval

SELECT 
    CASE
        WHEN Applicant_Age BETWEEN 18 AND 30 THEN '18-30'
        WHEN Applicant_Age BETWEEN 31 AND 40 THEN '31-40'
        WHEN Applicant_Age BETWEEN 41 AND 50 THEN '41-50'
        ELSE '50+' 
    END AS Age_Group,
    CASE
        WHEN Years_of_Working < 5 THEN 'Novice'
        WHEN Years_of_Working BETWEEN 5 AND 10 THEN 'Intermediate'
        ELSE 'Veteran'
    END AS Experience_Level,
    COUNT(*) AS Total_Applicants,
    SUM(CASE WHEN Status = 1 THEN 1 ELSE 0 END) AS Approved,
    ROUND((SUM(CASE WHEN Status = 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(*)) * 100, 2) AS Approval_Rate
FROM 
    credit_card_approval_status.applicant_details
GROUP BY 
    CASE
        WHEN Applicant_Age BETWEEN 18 AND 30 THEN '18-30'
        WHEN Applicant_Age BETWEEN 31 AND 40 THEN '31-40'
        WHEN Applicant_Age BETWEEN 41 AND 50 THEN '41-50'
        ELSE '50+' 
    END,
    CASE
        WHEN Years_of_Working < 5 THEN 'Novice'
        WHEN Years_of_Working BETWEEN 5 AND 10 THEN 'Intermediate'
        ELSE 'Veteran'
    END;

# 10. Correlation Between Total Bad Debt and Credit Card Approval

SELECT 
    CASE 
        WHEN Total_Bad_Debt > 0 THEN 'Has Bad Debt'
        ELSE 'No Bad Debt'
    END AS Debt_Status,
    COUNT(*) AS Total_Applicants,
    SUM(CASE WHEN Status = 1 THEN 1 ELSE 0 END) AS Approved,
    ROUND((SUM(CASE WHEN Status = 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(*)) * 100, 2) AS Approval_Rate
FROM 
    credit_card_approval_status.applicant_details
GROUP BY 
    CASE 
        WHEN Total_Bad_Debt > 0 THEN 'Has Bad Debt'
        ELSE 'No Bad Debt'
    END;







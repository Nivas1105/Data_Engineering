# Analysing Twitter Insights with AWS OpenSearch (Ongoing Project)
### Project Overview
This ongoing project aims to optimize search functionality for a web application using a large-scale Twitter dataset. The project integrates AWS OpenSearch Service along with AWS Lambda to enhance the performance, scalability, and security of the search process. By utilizing AWS services, the goal is to build a robust, cloud-based search solution capable of efficiently processing and querying massive volumes of Twitter data.
### Architecture Diagram:
![image](https://github.com/user-attachments/assets/6266e442-0efd-496a-b569-d70e7184a54d)
### Key Technologies
 - AWS OpenSearch Service: Utilized for efficient, real-time search and indexing of the Twitter dataset.
 - AWS Lambda: Serverless computing service used for processing and querying data dynamically.
 - Twitter Dataset: A dataset consisting of 100 tweets pulled every 20-25 days using a free Twitter API subscription, providing insights into trends, sentiments, and key topics
### Current Progress
1. Integration of AWS OpenSearch Service for indexing and querying Twitter data.
2. Lambda functions implemented for optimized data processing.
3. Enhancements in search performance and scalability through AWS infrastructure.
### Future Work
1. Integrate AWS Lambda with API Gateway: Set up API Gateway to expose Lambda functions for real-time data processing and interaction with the front-end.
2. Add Plotly for Data Visualization: Implement Plotly in the front-end to visualize search results and trends dynamically, providing an interactive experience for users.
### Installation
To set up and retrieve Twitter data for this project, follow the instructions below:
1. Set up a Twitter Developer Account:
Go to the Twitter Developer Portal and create a developer account.
Create a new Twitter app and obtain your API keys and access tokens (API Key, API Secret Key, Access Token, Access Token Secret).
2. Install twarc for Data Collection:
Follow the guide provided in this Twarc FAS Setup Tutorial to install and set up twarc, a command-line tool to collect Twitter data using the Twitter API.
pip install twarc
3. Configure twarc with Twitter API Keys:

After installing twarc, configure it with your Twitter credentials:
twarc configure
Enter your API keys and access tokens when prompted.

4. Collect Twitter Data:
Use twarc to collect tweets by specifying a search term or hashtag:

twarc search "your search query" > tweets.json
This will collect tweets based on your search term and save them in tweets.json.

5. Set up AWS OpenSearch:
Follow the AWS OpenSearch documentation to set up an OpenSearch domain for storing and indexing your Twitter dataset.

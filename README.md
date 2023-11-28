# StarNavi

Social Network: 

    This project is a simple REST API for a social network, implemented using the Flask framework. It includes basic models such as User and Post, where each post is created by a user. The main features of the API include user signup, user login, post creation, post like, and post unlike functionalities.

Additionally, the API offers analytics features, allowing users to retrieve information on the number of likes made within a specified date range. For example, the endpoint /api/analytics/?date_from=2020-02-02&date_to=2020-02-15 returns analytics aggregated by day.

Furthermore, the API provides a user activity endpoint, which displays the user's last login time and the timestamp of their last request to the service. This information can be useful for tracking user engagement and activity within the social network. The implementation leverages the Flask framework along with relevant libraries to achieve these functionalities.

Automated bot:

  The automated bot is designed to showcase system functionalities based on predefined rules. These rules are specified in a configuration file, and the bot utilizes the information within this file to simulate user activities. The configuration file includes the following integer fields 

number_of_users: Specifies the total number of users to be signed up.
max_posts_per_user: Defines the maximum number of posts each user can create.
max_likes_per_user: Sets the maximum number of likes each user can give.
The bot performs the following activities based on the provided configuration:

User Signup:
The bot initiates the signup process for the specified number of users mentioned in the configuration.

Post Creation:
Each signed-up user generates a random number of posts with diverse content, up to the maximum defined by max_posts_per_user.

Likes on Posts:
Following the signup and posting activities, the bot randomly assigns likes to posts. Posts have the potential to receive multiple likes from different users.

The purpose of the automated bot is to automate user interactions and demonstrate various functionalities within the system based on the provided configuration. The bot's actions mimic real user behavior, covering user registration, content creation, and engagement through likes on posts. The configuration file serves as a flexible tool to adjust parameters and observe the system's behavior under different scenarios.






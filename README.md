<br />
<div align="center">
  <h3 align="center">Olympics Video Classification
  <p align="center">
    Categorize Olympic sports using video clips with Twelve Labs
    <br />
    <a href="https://github.com/lewys-miugo/TwelveLabs-Olympics-App"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://sports-detector.streamlit.app/">View Demo</a>
    ·
    <a href="https://github.com/lewys-miugo/TwelveLabs-Olympics-App/issues">Report Bug</a>
    ·
    <a href="https://github.com/lewys-miugo/TwelveLabs-Olympics-App/issues">Request Feature</a>
  </p>
</div>



<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#About">About</a></li>
    <li><a href="#Features">Features</a></li>
    <li><a href="#Tech-Stack">Tech Stack</a></li>
    <li><a href="#Instructions-on-running-project-locally">Instructions on running project locally</a></li>
        <li><a href="#Usecase">Feedback</a></li>
    <li><a href="#Feedback">Feedback</a></li>
  </ol>
</details>

------

## About

The Olympics Video Clips Classification Application is a powerful tool designed to categorize various Olympic sports using video clips. By leveraging Twelve Labs' Marengo 2.6 Embedding Model, this application provides accurate classification of Olympic sports based on visual content, conversation, and text in video.


## Demonstration

Try the Application Now -

<a href="https://twelvelabs-olympics-app.streamlit.app/" target="_blank" style="
    display: inline-block;
    padding: 12px 24px;
    font-size: 18px;
    font-weight: bold;
    color: #ffffff;
    background-color: #007bff;
    border: none;
    border-radius: 8px;
    text-align: center;
    text-decoration: none;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    transition: background-color 0.3s, box-shadow 0.3s;
">
    Olympics Classification App
</a>


[![Watch the video](https://img.youtube.com/vi/9f2mScVn5ck/hqdefault.jpg)](https://youtu.be/9f2mScVn5ck)


## Features

🏅 **Olympic Sports Classification**: Accurately categorize various Olympic sports from video clips.

🎥 **Video Analysis**: Twelve Labs' Marengo 2.6 Embedding Model for comprehensive video analysis.

🚀️**Custom Classes**:Custom Classes for the more personalized categorization.

## Tech Stack

**Frontend** - Streamlit

**Backend** -  Python 

**AI Technologies** - Twelve Labs Marengo 2.6 (Embedding Model)
 
**Deployment** - Streamlit Cloud

 
 ## Instructions on running project locally:
 
To get started with the Olympics Video Clips Classification Application, follow these steps -

Clone the project

Step 1 -

```bash
git clone https://github.com/lewys-miugo/TwelveLabs-Olympics-App.git
```

Step 2  -

Install dependencies:

```bash
 cd TwelveLabs-Olympics-App
 
 pip install -r requirements.txt
```

Step 3 - 

Set up your Twelve Labs account -

Create an account on the Twelve Labs Portal
Navigate to the Twelve Labs Playground
Create a new index and select Marengo 2.6 as the Embedding Model
Upload Olympic video clips to your index

![index-creation](https://github.com/lewys-miugo/TwelveLabs-Olympics-App/blob/main/src/index-creation.png)

Step 4 -

Get your API Key from the [Twelve Labs Dashboard](https://playground.twelvelabs.io/dashboard/api-key)
Find your INDEX_ID in the URL of your created [index](https://playground.twelvelabs.io/indexes/{index_id})

Step 5 -
Configure the application with your API credentials by creating .env and adding API_KEY, INDEX_KEY and STREAMLIT_APP_URL=http://localhost:8501/ NB: When hosting with Streamlit remember to put them in TOML format.

Step 6 -

Run the Streamlit application

```bash
  streamlit run app.py
```

Step 7 - 

Run the Server -

```bash
  http://localhost:8501/
```

## Usecases

🔍**Video Search Engine:** Create a searchable database of video content, allowing users to find specific scenes or topics within large video collections.

🎥**Security Footage Analyzer**
Detect and categorize specific events or behaviors in security camera footage.

💃 **Dance Move Classifier** Identify and categorize different dance styles or specific moves from dance videos.


## Feedback

If you have any feedback, please reach out to us at **lewiswambugu01@gmail.com**


## License

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## 👨‍💻 About the Developer

**Lewys Miugo**
- 📧 Email: lewysmiugo@gmail.com
- 🐙 GitHub: [@lewys-miugo](https://github.com/lewys-miugo)
- 💼 LinkedIn: [Connect with me](https://linkedin.com/in/lewys-miugo)

## 🙏 Credits

This project is based on the original work by **Hrishikesh Yadav**:
- 📧 Original Author: hriskikesh.yadav332@gmail.com
- 🐙 Original Repository: [TwelveLabs-Olympics-App](https://github.com/Hrishikesh332/TwelveLabs-Olympics-App)
- 💼 LinkedIn: [@hrishikesh332](https://linkedin.com/in/hrishikesh332)

Built with ❤️ using Twelve Labs AI and Streamlit

---

<div align="center">
  <p>⭐ Star this repository if you found it helpful!</p>
  <p>Made with 🏅</p>
</div>


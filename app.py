import streamlit as st
import csv
import xml.etree.ElementTree as ET
from io import StringIO
import pandas as pd

# Function to process tag block from text input
def process_tag_block(tag_block):
    tag_details = {}
    lines = tag_block.split('\n')
    for line in lines:
        if line.startswith('Tag Name:'):
            tag_details['Tag Name'] = line.replace('Tag Name:', '').strip()
        elif line.startswith('Tag Location:'):
            tag_details['Tag Location'] = line.replace('Tag Location:', '').strip()
        elif line.startswith('Created On:'):
            tag_details['Created On'] = line.replace('Created On:', '').strip()
        elif line.startswith('Paused:'):
            tag_details['Paused'] = line.replace('Paused:', '').strip()
        elif line.startswith('Tag:'):
            tag_index = lines.index(line)
            tag_content = '\n'.join(lines[tag_index+1:])
            tag_details['Tag'] = tag_content.strip()
            break
    page_conditional_lines = [line.replace('Page Conditionals:', '').strip() for line in lines if line.startswith('Page Conditionals:')]
    tag_details['Page Conditionals'] = ', '.join(page_conditional_lines) if page_conditional_lines else ''
    return tag_details

# Function to process XML for slides info
def process_slides_info(root):
    slides = []
    for item in root.findall('.//item'):
        slide = {
            'Title': item.find('title').text if item.find('title') is not None else '',
            'Link': item.find('link').text if item.find('link') is not None else ''
        }
        slides.append(slide)
    return pd.DataFrame(slides)

# Function to process XML for coupons info
def process_coupons_info(root):
    coupons = []
    for item in root.findall('.//item'):
        coupon = {
            'Title': item.find('title').text if item.find('title') is not None else '',
            'Link': item.find('link').text if item.find('link') is not None else ''
        }
        coupons.append(coupon)
    return pd.DataFrame(coupons)

# Function to process XML for staff info
def process_staff_info(root):
    staff = []
    for item in root.findall('.//item'):
        member = {
            'Name': item.find('title').text if item.find('title') is not None else ''
        }
        staff.append(member)
    return pd.DataFrame(staff)

# Function to process XML for redirect rules
def process_redirect_rules(root):
    rules = []
    for item in root.findall('.//item'):
        rule = {
            'Title': item.find('title').text if item.find('title') is not None else '',
            'Original URL': item.find('link').text if item.find('link') is not None else ''
        }
        rules.append(rule)
    return pd.DataFrame(rules)

# Streamlit UI setup
st.title("File Processor App")

# User selects the action
action = st.selectbox("Select the action you want to perform:", ["Process Tag Block", "Process Slides Info", "Process Coupons Info", "Process Staff Info", "Process Redirect Rules"])

# User uploads a file
uploaded_file = st.file_uploader("Choose a file", type=["txt", "xml"])

if uploaded_file is not None and st.button("Process"):
    if action == "Process Tag Block":
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        string_data = stringio.read()
        tags = [process_tag_block(tag_block) for tag_block in string_data.split("------------") if tag_block.strip()]
        df = pd.DataFrame(tags)
        st.dataframe(df)
    else:
        tree = ET.parse(uploaded_file)
        root = tree.getroot()

        if action == "Process Slides Info":
            df = process_slides_info(root)
        elif action == "Process Coupons Info":
            df = process_coupons_info(root)
        elif action == "Process Staff Info":
            df = process_staff_info(root)
        elif action == "Process Redirect Rules":
            df = process_redirect_rules(root)

        st.dataframe(df)

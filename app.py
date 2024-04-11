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
def process_coupons_info(root, namespaces):
    coupons_data = []
    for item in root.findall('.//item'):
        title = item.find('title').text if item.find('title') is not None else ''
        link = item.find('link').text if item.find('link') is not None else ''
        description = item.find('content:encoded', namespaces).text if item.find('content:encoded', namespaces) is not None else ''
        status = item.find('wp:status', namespaces).text if item.find('wp:status', namespaces) is not None else ''
        post_date = item.find('wp:post_date', namespaces).text if item.find('wp:post_date', namespaces) is not None else ''

        expiration_date = image_url = None
        for postmeta in item.findall('wp:postmeta', namespaces):
            meta_key = postmeta.find('wp:meta_key', namespaces).text
            meta_value = postmeta.find('wp:meta_value', namespaces).text
            if meta_key == 'expiration_date':
                expiration_date = meta_value
            elif meta_key == 'post_banner_url':
                image_url = meta_value

        coupons_data.append({
            'Title': title, 'Link': link, 'Description': description, 'Expiration Date': expiration_date,
            'Image URL': image_url, 'Status': status, 'Post Date': post_date
        })

    return pd.DataFrame(coupons_data)


# Function to process XML for staff info
def process_staff_info(root, namespaces):
    staff_data = []
    for item in root.findall('.//item'):
        name = title = phone = email = department = ''
        title_text = item.find('title').text if item.find('title') is not None else ''
        name = title_text.split(',')[0] if ',' in title_text else title_text

        for postmeta in item.findall('wp:postmeta', namespaces):
            meta_key = postmeta.find('wp:meta_key', namespaces).text
            meta_value = postmeta.find('wp:meta_value', namespaces).text
            if meta_key == 'title':
                title = meta_value
            elif meta_key == 'phone':
                phone = meta_value
            elif meta_key == 'email':
                email = meta_value
            elif meta_key == 'department':
                department = meta_value

        staff_data.append({'Name': name, 'Title': title, 'Phone': phone, 'Email': email, 'Department': department})

    return pd.DataFrame(staff_data)


# Function to process XML for redirect rules
def process_redirect_rules(root, namespaces):
    rules_data = []
    for item in root.findall('.//item'):
        title = item.find('title').text if item.find('title') is not None else ''

        original_url = redirected_url = None
        for postmeta in item.findall('wp:postmeta', namespaces):
            meta_key = postmeta.find('wp:meta_key', namespaces).text
            meta_value = postmeta.find('wp:meta_value', namespaces).text
            if meta_key == '_redirect_rule_from':
                original_url = meta_value
            elif meta_key == '_redirect_rule_to':
                redirected_url = meta_value

        if original_url and redirected_url:
            rules_data.append({'Title': title, 'Original URL': original_url, 'Redirected URL': redirected_url})

    return pd.DataFrame(rules_data)


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

import streamlit as st
import boto3
import json
import random

# Configure the boto3 client with the retrieved credentials
s3 = boto3.client(
    "s3",
    aws_access_key_id=st.secrets["AWS"]["aws_access_key_id"],
    aws_secret_access_key=st.secrets["AWS"]["aws_secret_access_key"]
)
bucket_name = st.secrets["AWS"]["bucket_name"]

def save_collection_to_s3(user_id, collection_data):
    file_name = f"{user_id}_collection.json"
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=json.dumps(collection_data))

def load_collection_from_s3(user_id):
    file_name = f"{user_id}_collection.json"
    try:
        obj = s3.get_object(Bucket=bucket_name, Key=file_name)
        return json.loads(obj['Body'].read())
    except s3.exceptions.NoSuchKey:
        return []

user_id = "user@example.com"
user_collection = load_collection_from_s3(user_id)

st.title("URL and File Node Visualization")
st.header("Add Nodes")

node_type = st.selectbox("Node Type", ["URL", "Video", "File", "Image"])
node_name = st.text_input("Node Name", "")
node_topic = st.text_input("Node Topic", "")

if node_type == "URL":
    node_url = st.text_input("URL", "")
elif node_type == "Video":
    node_video = st.text_input("Video URL", "")
elif node_type == "File":
    node_file = st.file_uploader("Upload File", type=["pdf", "docx", "txt"])
elif node_type == "Image":
    node_image = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

add_node_button = st.button("Add Node")

if add_node_button:
    new_node = {"id": len(user_collection) + 1, "type": node_type, "name": node_name, "topic": node_topic, "x": random.randint(50, 750), "y": random.randint(50, 550)}
    if node_type == "URL":
        new_node["content"] = node_url
    elif node_type == "Video":
        new_node["content"] = node_video
    elif node_type == "File" and node_file:
        file_key = f"{node_name}-{node_file.name}"
        s3.upload_fileobj(node_file, bucket_name, file_key)
        new_node["content"] = file_key
        st.success(f"File {node_file.name} uploaded successfully!")
    elif node_type == "Image" and node_image:
        image_key = f"{node_name}-{node_image.name}"
        s3.upload_fileobj(node_image, bucket_name, image_key)
        new_node["content"] = image_key
        st.success(f"Image {node_image.name} uploaded successfully!")
    user_collection.append(new_node)
    save_collection_to_s3(user_id, user_collection)

st.header("Node Visualization")

# Prepare the node data in Python
node_data = json.dumps(user_collection)

# Embed the node data into the D3.js code
markdown_key = f"graph-{len(user_collection)}"
d3_html = f"""
<div id='d3-container'></div>
<script src='https://d3js.org/d3.v7.min.js'></script>
<script>
const data = {node_data};
function updateVisualization() {{
    d3.select('#d3-container').selectAll('*').remove();
    const svg = d3.select('#d3-container').append('svg').attr('width', 800).attr('height', 600);
    const nodes = svg.selectAll('circle').data(data, d => d.id);
    nodes.enter().append('circle').attr('cx', d => d.x).attr('cy', d => d.y).attr('r', 20).style('fill', d => getNodeColor(d.type));
    nodes.exit().remove();
    nodes.on('click', d => {{ alert('Node Clicked: ' + d.content); }});
}}
function getNodeColor(type) {{
    switch (type) {{
        case 'URL': return 'blue';
        case 'Video': return 'green';
        case 'File': return 'orange';
        case 'Image': return 'red';
        default: return 'gray';
    }}
}}
updateVisualization();
</script>
"""
st.markdown(d3_html, unsafe_allow_html=True, key=markdown_key)

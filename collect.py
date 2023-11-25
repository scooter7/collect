import streamlit as st
import boto3

# Configure the boto3 client with the retrieved credentials
s3 = boto3.client("s3", aws_access_key_id=st.secrets["AWS"]["aws_access_key_id"], aws_secret_access_key=st.secrets["AWS"]["aws_secret_access_key"])
bucket_name = st.secrets["AWS"]["bucket_name"]
object_key = st.secrets["AWS"]["object_key"]

# Function to save collection to S3
def save_collection_to_s3(user_id, collection_data):
    file_name = f"{user_id}_collection.json"
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=json.dumps(collection_data))

# Function to load collection from S3
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

st.header("Node Visualization")

d3_html = """
<div id="d3-container"></div>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const data = [];
function updateVisualization() {
    const svg = d3.select("#d3-container").append("svg").attr("width", 800).attr("height", 600);
    const nodes = svg.selectAll("circle").data(data, d => d.id);
    nodes.enter().append("circle").attr("cx", d => d.x).attr("cy", d => d.y).attr("r", 20).style("fill", d => getNodeColor(d.type));
    nodes.exit().remove();
    nodes.on("click", d => { alert("Node Clicked: " + d.content); });
}
function getNodeColor(type) {
    switch (type) {
        case "URL": return "blue";
        case "Video": return "green";
        case "File": return "orange";
        case "Image": return "red";
        default: return "gray";
    }
}
updateVisualization();
</script>
"""
components.html(d3_html, height=600)

if add_node_button:
    if node_type == "URL":
        user_collection.append({"id": len(user_collection) + 1, "x": 100, "y": 100, "type": "URL", "content": node_url})
    elif node_type == "Video":
        user_collection.append({"id": len(user_collection) + 1, "x": 200, "y": 200, "type": "Video", "content": node_video})
    elif node_type == "File" and node_file:
        file_key = f"{node_name}-{node_file.name}"
        s3.upload_fileobj(node_file, bucket_name, file_key)
        user_collection.append({"id": len(user_collection) + 1, "x": 300, "y": 300, "type": "File", "content": file_key})
        st.success(f"File {node_file.name} uploaded successfully!")
    elif node_type == "Image" and node_image:
        image_key = f"{node_name}-{node_image.name}"
        s3.upload_fileobj(node_image, bucket_name, image_key)
        user_collection.append({"id": len(user_collection) + 1, "x": 400, "y": 400, "type": "Image", "content": image_key})
        st.success(f"Image {node_image.name} uploaded successfully!")
    save_collection_to_s3(user_id, user_collection)
    updateVisualization()

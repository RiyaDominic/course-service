import os
import boto3
from flask import Flask, jsonify
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

app = Flask(__name__)

# Configure AWS X-Ray
xray_recorder.configure(service="course-service")
XRayMiddleware(app, xray_recorder)

# AWS Region
REGION = os.environ.get("AWS_REGION", "us-east-1")

# DynamoDB setup
dynamodb = boto3.resource("dynamodb", region_name=REGION)
courses_table = dynamodb.Table("Riya_Course")


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "course-service"
    }), 200


@app.route("/courses/<course_code>", methods=["GET"])
def get_course(id):
    try:
        resp = courses_table.get_item(Key={"id": id})
        item = resp.get("Item")

        if not item:
            return jsonify({
                "error": "Course not found"
            }), 404

        return jsonify(item), 200

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route("/courses", methods=["GET"])
def list_courses():
    try:
        resp = courses_table.scan(Limit=50)

        return jsonify(resp.get("Items", [])), 200

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=3001,
        debug=False
    )
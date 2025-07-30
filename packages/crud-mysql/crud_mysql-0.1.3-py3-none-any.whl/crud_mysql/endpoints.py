from flask import Blueprint
from flask import request, jsonify
from .crud_object import CrudObject

crud = Blueprint('crud', __name__, template_folder='templates')

@crud.route("/<object_type>", methods=["GET"])
def get_object(object_type):
	try:
		crud_object = CrudObject(object_type)
		object_id = request.args.get(f"{object_type}_id")
		if not object_id:
			return(f"no {object_type} id was provided. (add {object_type}_id argument)"), 400
		try:
			object_obj = crud_object.get_object(object_id)
			if object_obj:
				return jsonify(object_obj), 200
			else:
				return jsonify("object not found"), 400
		except Exception as e:
			return jsonify("object not found"), 400
	except Exception as e:
		try:
			crud_object = CrudObject(object_type[0:-1])
			if object_type.endswith('s') and crud_object.fetch_all:
				filter = request.args.get("filter", "")
				objects = crud_object.get_objects(filter)
				return jsonify(objects), 200
			else:
				raise
		except Exception as e:
			return jsonify(f"Invalid path: /{object_type}"), 404
	
	
@crud.route("/<object_type>", methods=["POST"])
def create_object(object_type):
	try:
		crud_object = CrudObject(object_type)
	except:
		return jsonify(f"Invalid path: /{object_type}"), 404
	if "POST" not in crud_object.allowd_methods:
		return jsonify("method not allowed"), 400
	data = request.json
	if not object_type in data:
		return jsonify(f"missing {object_type} info. (add {object_type} object in body)"), 400
	object_info = data[object_type]
	object_id = crud_object.create_object(object_info)
	if object_id:
		return jsonify({"objectId": object_id}), 201
	else:
		return jsonify("error occured while creating object"), 500
	
@crud.route("/<object_type>", methods=["PUT"])
def update_object(object_type):
	try:
		crud_object = CrudObject(object_type)
	except:
		return jsonify(f"Invalid path: /{object_type}"), 404
	if "PUT" not in crud_object.allowd_methods:
		return jsonify("method not allowed"), 400
	object_id = request.args.get(f"{object_type}_id")
	data = request.json
	if not object_type in data:
		return jsonify(f"missing {object_type} info to change. (add {object_type} object in body)"), 400
	object_info = data[object_type]
	crud_object.update_object(object_id, object_info)
	return jsonify(f"Successfully updated {object_type} with id: {object_id}"), 200

@crud.route("/<object_type>", methods=["DELETE"])
def delete_object(object_type):
	try:
		crud_object = CrudObject(object_type)
	except:
		return jsonify(f"Invalid path: /{object_type}"), 404
	if "DELETE" not in crud_object.allowd_methods:
		return jsonify("method not allowed"), 400
	object_id = request.args.get(f"{object_type}_id")
	crud_object.delete_object(object_id)
	return jsonify(f"Successfully deleted {object_type} with id: {object_id}"), 204
from flask import jsonify

class ResponseBuilder:
    @staticmethod
    def get(msg = None, data = None):
        if data == []:
            return jsonify({'msg': msg}), 200
        
        else:
            return jsonify({'data': data}), 200
        
    @staticmethod
    def put(msg, data=None):
        return jsonify({'msg': msg, 'data': data}), 200

    @staticmethod
    def post(msg, data = None):
        if data:
            return jsonify({'msg': msg, 'data': data}), 201
        
        else:
            return jsonify({'msg': msg}), 201
        
    @staticmethod
    def delete(msg):
        return jsonify({'msg': msg}), 200
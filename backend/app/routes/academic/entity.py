from flask import Blueprint
from app.utils import required_role, validate_input, ResponseBuilder, with_log
from flask_jwt_extended import jwt_required, get_jwt
from app.schemas import AcademicShowSchemas, AcademicUpdateSchemas, AcademicSchemas
from app.services import Academic_Score_Service, Score_Workflow, Academic_Schedule_Service
from app.extensions import db
from app.repositories import Repositories

academic_entity_bp = Blueprint('academic_entity_bp', __name__, url_prefix = '/api/academic/entity')
academic_score_service = Academic_Score_Service(db, Repositories)
academic_schedule_service = Academic_Schedule_Service(db, Repositories)
score_workflow = Score_Workflow(db, Repositories)

@academic_entity_bp.get('/lessons/<int:id>/scores')
@jwt_required()
@required_role('admin', 'Teacher')
@validate_input(AcademicShowSchemas.Scores)
def show_scores_by_class_room_route(id: int, validated_data):
    #lấy học sinh, điểm theo lớp, môn
    validated_data['lesson_id'] = id
    result = score_workflow.process_show_students_for_give_score(validated_data)
    msg = 'Không tìm thấy thông tin!'
    return ResponseBuilder.get(msg, result)

@academic_entity_bp.put('/scores')
@jwt_required()
@required_role('admin', 'Teacher')
@validate_input(AcademicUpdateSchemas.Scores)
def give_scores_route(validated_data):
    result = score_workflow.process_add_scores(validated_data, get_jwt().get('id'))
    msg = f'Đã cho điểm cho học sinh {result}!'
    return ResponseBuilder.put(msg)

@academic_entity_bp.put('/scores/lessons/summary')
@jwt_required()
@required_role('admin', 'Teacher')
@validate_input(AcademicUpdateSchemas.SummaryLessonPeriod)
def summary_lesson_for_student(validated_data):
    score_workflow.process_summary_semester_lessons_result(validated_data, get_jwt().get('id'))
    msg = 'Đã tổng kết!'
    return ResponseBuilder.put(msg)

@academic_entity_bp.put('semesters/<int:id>/summary')
@jwt_required()
@required_role('admin', 'Teacher')
@validate_input(AcademicUpdateSchemas.SummaryPeriod)
def summary_semester_for_students(id, validated_data):
    validated_data['semester_id'] = id
    score_workflow.process_summary_semester_result(validated_data, get_jwt().get('id'))
    msg = 'Đã tổng kết!'
    return ResponseBuilder.put(msg)

@academic_entity_bp.put('years/<int:id>/summary')
@jwt_required()
@required_role('admin', 'Teacher')
@validate_input(AcademicUpdateSchemas.SummaryYear)
def summary_year_for_students(id, validated_data):
    validated_data['year_id'] = id
    score_workflow.process_summary_year_result(validated_data, get_jwt().get('id'))
    msg = 'Đã tổng kết năm học!'
    return ResponseBuilder.post(msg)

@academic_entity_bp.get('/schedules')
@jwt_required()
@required_role('admin')
@validate_input(AcademicShowSchemas.Schedule)
def get_schedules(validated_data):
    result = academic_schedule_service.handle_show_schedules(validated_data)
    msg = 'Không tìm thấy thông tin!'
    return ResponseBuilder.get(msg, result)

@academic_entity_bp.post('/schedules')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.Schedule)
def create_schedule_route(validated_data):
    academic_schedule_service.handle_add_schedule(validated_data, get_jwt().get('id'))
    msg = f"Đã thêm thời khóa biểu!"
    return ResponseBuilder.post(msg)


    


 
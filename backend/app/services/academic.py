from app.utils import get_updated_fields
from .base import BaseService
from .subservices.sub_academic import AcademicCheck, AcademicGet

class AcademicAddService(BaseService):
    def __init__(self, db, get_repo, add_repo, check_repo):
        self.db = db
        self.get_repo = get_repo(db)
        self.add_repo = add_repo(db)
        self.check_repo = check_repo(db)
        self.academic_check = AcademicCheck(self.check_repo)
        self.academic_get = AcademicGet(self.get_repo)

    def handle_add_year(self, data: dict):       
        #check dup
        self.academic_check.dup_year(data)

        self.add_repo.year(data)
        self.db.session.commit()
        return {'data': data['year']}
         
    def handle_add_semester(self, data: dict):        
        self.academic_check.dup_semester(data)
        
        self.add_repo.semester(data)
        self.db.session.commit()
        return {'data': data['semester']}
         
    def handle_add_lesson(self, data: dict):        
        self.academic_check.dup_lesson(data)
 
        data['class_room_id'] = self.get_repo.class_room_by_grade_id(data)
        self.add_repo.lesson(data)
        self.db.session.commit()
        return {'data': data['lesson']}
        
    def handle_add_grade(self, data: dict):       
        self.academic_check.dup_grade(data)

        self.add_repo.grade(data)
        self.db.session.commit()
        return {'data': data['grade']}
  
    def handle_add_class_room(self, data: dict):  
        #check year
        self.academic_get.year_id(data)
        #check class_room
        self.academic_check.dup_class_room(data)
        
        self.add_repo.class_room(data)
        self.db.session.commit()
        return {'data': data['class_room']}
        

    def handle_add_schedule(self, data: dict):
        pass


    def handle_add_scores(self, data: dict):
        #check semester id
        self.academic_get.semester_id(data)
        #check year id
        self.academic_get.year_id(data)
        #get period_id by semester_id & year_id
        period_id = self.get_repo.get_period_id(data)
        print(period_id)
        #get student_lesson_id
        return data

class AcademicShowService(BaseService):
    def __init__(self, db, repo):
        self.repo_show = repo(db)

    def handle_show_year(self, data: dict):
        result = self.repo_show.year(data)
        keys = ['id', 'year']
        if result: return [dict(zip(keys, values)) for values in result]

    def handle_show_semester(self, data: dict):
        result = self.repo_show.semester(data)
        keys = ['semester_id', 'semester']
        if result: return [dict(zip(keys, values)) for values in result]
        
    def handle_show_grade(self, data: dict):
            result = self.repo_show.grade(data)
            keys = ['id', 'grade']
            if result: return [dict(zip(keys, values)) for values in result]
              
    def handle_show_lesson(self, data:dict):
            keys = ['lesson_id', 'lesson', 'grade', 'grade_id']
            if data['role'] == 'admin': 
                if result := self.repo_show.lesson(data): 
                    return [dict(zip(keys, values)) for values in result]
            
            # elif role == 'Teacher':
            #     if result:= self.repo_show_repo.show_lesson_by_id(id, lesson_data.lesson): 
            #         return {'status': 'Success', 'data': [dict(zip(keys, values)) for values in result]}

    def handle_show_class_room(self, data: dict):  
            result = self.repo_show.class_room(data)
            keys = ['class_room_id', 'class_room']
            if result: 
                return [dict(zip(keys, values)) for values in result]
        
    def handle_show_teach_room(self, data: dict):
            print(data)
            if data['role'] == 'admin': 
                 result = self.repo_show.class_room(data)
            
            elif data['role'] == 'Teacher': 
                 result = self.repo_show.teach_room(data) 
            
            keys = ['class_room_id', 'class_room', 'grade_id', 'teacher_id']

            if result: return [dict(zip(keys, values)) for values in result]

    def handle_show_teach_class_with_teacher_id_by_lesson_id(self, data: dict):
            keys = ['class_room_id', 'lesson_id', 'teacher_id', 'class_room', 'teacher']
            if result := self.repo_show.teach_class_with_teacher_id_by_lesson_id(data):
                return [dict(zip(keys, values)) for values in result]

class AcademicDelService(BaseService):
    pass

class AcademicUpdateService(BaseService):
    def __init__(self, db, get_repo, update_repo, check_repo):
        super().__init__(db)
        self.get_repo = get_repo(db)
        self.update_repo = update_repo(db)
        self.check_repo = check_repo(db)
        self.academic_check = AcademicCheck(self.check_repo)
        self.academic_get = AcademicGet(self.get_repo)

    def handle_update_lesson(self, data):
        for new in data:
            #check ID
            current = self.academic_get.lesson_id(new)
            current_dict = {'lesson': current.lesson, 'grade_id': current.grade_id}

            update = get_updated_fields(new, current_dict)
            update['lesson_id'] = new['lesson_id']

            if update.get('lesson'):
                #check duplicated name
                self.academic_check.dup_lesson(update)
                current.lesson = update['lesson']

            if update.get('grade_id'):
                current.grade_id = update['grade_id']
                
                class_room = self.get_repo.class_room_by_grade_id(update)
                update['year_id'] = new['year_id']
                update['class_room_id'] = [item[0] for item in class_room]
                self.update_repo.class_lesson_by_lesson_id(update)
            
        lesson = ', '.join(item['lesson'] for item in data)
          
        self.db.session.commit()
        return {'lesson': lesson}
        
    def handle_update_class_room(self, data):
        for new in data:
            #check ID
            class_room_id = self.academic_get.class_room_id(new)

            #check duplicated name
            self.academic_check.dup_class_room(new)

            #update to db
            class_room_id.class_room = new['class_room']
            self.db.session.commit()

            class_room = ', '.join(item['class_room'] for item in data)
        return {'class_room': class_room}
    
    def handle_set_year(self, data: dict):
        #Chuyển tất cả về False
        self.update_repo.update_year_status()
        #Chuyển selected year về True
        year = self.get_repo.year_by_id(data)
        year.is_active = True
        self.db.session.commit()
        return year
    
    def handle_update_semester(self, data: dict):
        for new in data:
            semester_id = self.get_repo.semester_by_id(new)
            #check dup name
            self.academic_check.dup_semester(new)

            semester_id.semester = new['semester']
            self.db.session.commit()

            semester = ', '.join(item['semester'] for item in data)
        return {'semester': semester}
    
    def handle_assign_student_to_class(self, data):
        #check class id
        self.academic_get.class_room_id(data)
        #update student class 
        self.get_repo.assign_student_class_by_student_id(data)
        self.db.session.commit()

        return data
             



            

        


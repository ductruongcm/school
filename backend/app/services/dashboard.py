import pandas as pd
import numpy as np

class Dashboard_Service:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.dashboard_repo = self.repo.dashboard

    def handle_show_class_room_infos_by_year(self, data):
        student_academic = self.dashboard_repo.get_academic_student_for_class_by_period(data)
        df = pd.DataFrame(student_academic, columns=['class_room_id', 'student_id', 'avg']).sort_values(['student_id'])
        df = df.groupby(['class_room_id', 'student_id'])['avg'].min().reset_index()

        condition = [df['avg'] < 5,
                     (df['avg'] >= 5) & (df['avg'] < 6.5),
                     (df['avg'] >= 6.5) & (df['avg'] < 8)]
        
        choices = ['bad', 'tb', 'good']

        df['rank'] = np.select(condition, choices, default='exec')
        
        df = df.groupby('class_room_id')['rank'].value_counts().unstack(fill_value=0).reset_index()

        info = self.dashboard_repo.show_class_rooms_info_by_year(data)
        info_df = pd.DataFrame(info, columns=['class_room_id', 'class_room', 'qty', 'teacher']).fillna(0).astype(int, errors='ignore')

        result = info_df.merge(df, on = 'class_room_id', how='left').fillna(0).astype(int, errors='ignore').to_dict(orient='records')
        return result
    

    def handle_show_summary_info_by_year(self, data):
        summary = self.dashboard_repo.get_summary_by_year_semester(data)
        keys = ['count_class', 'count_teacher', 'count_student10', 'count_student11', 'count_student12', 'count_students']
        result = dict(zip(keys, summary))
        return result
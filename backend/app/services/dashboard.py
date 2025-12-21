import pandas as pd
import numpy as np
from ..exceptions import CustomException

class Dashboard_Service:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.dashboard_repo = self.repo.dashboard

    def handle_show_daily_class_room_infos(self, data):
        student_academic = self.dashboard_repo.get_academic_student_for_class_by_period(data)
        if not student_academic:
            raise CustomException('Chưa có dữ liệu!')
    
        df = pd.DataFrame(student_academic, columns=['class_room_id', 'student_id', 'avgs'])
        if df['avgs'].apply(lambda x: any(i is None for i in x)).any():
            df['learning_status'] = '-'

        else:
            score_matrix = np.array(df['avgs'].to_list(), dtype=float)
            score_matrix = np.nan_to_num(score_matrix, nan=-1)
            
            num_subjs = score_matrix.shape[1]
            min_required_subjs = num_subjs - 1
            
            cond_good = ((score_matrix >= 6.5).all(axis=1) & (np.sum(score_matrix >= 8, axis=1) >= 6))

            cond_fair_A = ((np.sum(score_matrix >= 6.5, axis=1) == min_required_subjs) & (np.sum(score_matrix >= 8, axis=1) >= 6) & (np.sum(score_matrix < 6.5, axis=1) == 1))
            cond_fair_B = ((score_matrix >= 5).all(axis=1) & (np.sum(score_matrix >= 6.5, axis = 1) >= 6))
            cond_fair = cond_fair_A | cond_fair_B
            
            cond_avg_A = ((score_matrix >= 3.5).all(axis=1) & (np.sum(score_matrix >= 5, axis = 1) >= 6))
            cond_avg_B = ((np.sum(score_matrix >= 6.5, axis = 1) == min_required_subjs) & (np.sum(score_matrix >= 8, axis = 1) >= 8) & (np.sum(score_matrix < 5, axis = 1) == 1))
            cond_avg_C = ((np.sum(score_matrix >= 5, axis = 1) == min_required_subjs) & (np.sum(score_matrix >= 6.5, axis = 1) >= 6) & (np.sum(score_matrix < 5, axis = 1) == 1))
            cond_avg = cond_avg_A | cond_avg_B | cond_avg_C
            
            choices = ['good', 'fair', 'avg']

            df['learning_status'] = np.select([cond_good, cond_fair, cond_avg], choices, default = 'bad')

        ranking_count_df = pd.crosstab(index=df['class_room_id'], columns=df['learning_status']).reset_index().fillna(0).astype('Int64')
   
        info = self.dashboard_repo.show_class_rooms_info_daily(data)
        info_df = pd.DataFrame(info, columns=['class_room_id', 'class_room', 'qty', 'absence_e', 'absence_a','teacher'])
        result_df = info_df.merge(ranking_count_df, on = 'class_room_id', how='left').replace({np.nan: None})

        result = result_df.to_dict(orient='records')
        print(result_df)
        return result
    
    def handle_show_summary_info_by_year(self, data):
        summary = self.dashboard_repo.get_summary_by_year_semester(data)
        keys = ['count_class', 'count_teacher', 'count_student10', 'count_student11', 'count_student12', 'count_students']
        result = dict(zip(keys, summary))
        return result
    
    def handle_show_year_summary_result(self, data):
        result = self.dashboard_repo.get_report_of_year_summary_result(data)
        keys = ['total', 'graduation', 'upgrade', 'failure', 'retest', 'good', 'fair', 'avg', 'new', 'transfer']
        output = dict(zip(keys, result))
        print(output)
        return output
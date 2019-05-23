from datetime import timedelta, date
from dbconn import DBConn


class Mood(DBConn):

    def get_max_streak_percentile(self, user_id):
        max_streak = self.query_db('select max_streak from users where UserID=?', args=(user_id,), one=True)
        if max_streak is False:
            return False
        all_max_streaks = self.query_db('select distinct max_streak from users')
        if all_max_streaks is False:
            return False
        # unpack and sort the list
        streak_range = sorted([streak[0] for streak in all_max_streaks])
        return ((streak_range.index(max_streak[0]) + 1) / len(streak_range)) * 100

    def get_streak(self, user_id):
        """
        queries the DB for the current streak and the streak's expiration date
        if the streak has expired, updates the streak to 0
        otherwise returns the streak
        returns false in the case of a db error
        """
        streak_data = self.query_db('select streak, streak_exp, max_streak from users where UserID=?', args=(user_id,), one=True)
        if streak_data:
            streak, exp_date, max_streak = streak_data
            if exp_date < self.date_stamp():
                # streak is expired
                if self.update_streak(user_id, 0, max_streak) is not False:
                    return 0
            else:
                return streak
        return False

    def get_moods(self, user_id):
        """
        returns list of all moods associated with this user ID
        returns False in case of error
        """
        return self.query_db('select distinct mood from moods where UserID=?', args=(user_id,))

    def save_mood(self, user_id, mood):
        """
        creates a mood record in the DB with today's date and associated with a specific user
        """
        streak = self.check_and_update_streak(user_id)
        if streak is False:
            return False
        print("streak updated successfully")
        if self.edit_db('insert into moods values(?, ?, ?)', args=(
            user_id,
            self.date_stamp(),
            mood
        )):
            return streak
        return False

    def check_and_update_streak(self, user_id):
        """
        returns streak
        returns False in case of DB error
        run on mood submission
        check for a mood yesterday and today
               mood yesterday AND no mood today: pull the current user's streak, increment it, save it back to the DB
            no mood yesterday AND no mood today: set the current user's streak to 1
               mood yesterday AND mood today: already on streak, do nothing
            no mood yesterday AND mood today: already on streak, do nothing
        """
        streak_data = self.query_db('select streak, max_streak from users where UserID=?', args=(user_id,), one=True)
        if streak_data is False:
            return False
        streak, max_streak = streak_data
        if self.did_submit_today(user_id):
            # user is already submitted a mood today
            return streak
        # user has not submitted yet for today
        if self.did_submit_yesterday(user_id):
            streak += 1
            # user submitted yesterday
            if self.update_streak(user_id, streak, max_streak):
                return streak
        # user has not submitted yesterday or today
        # set streak to 1
        if self.update_streak(user_id, 1, max_streak):
            return 1
        return False

    def did_submit_yesterday(self, user_id):
        count = self.query_db('select count(*) from moods where UserID=? and Datetime=?', args=(user_id, self.date_stamp(days=-1)), one=True)
        if count is not False:
            if count[0] > 0:
                return True
        return False

    def did_submit_today(self, user_id):
        count = self.query_db('select count(*) from moods where UserID=? and Datetime=?', args=(user_id, self.date_stamp()), one=True)
        if count is not False:
            if count[0] > 0:
                return True
        return False

    def update_streak(self, user_id, streak, max_streak):
        """
        helper that updates and returns streak
        updates max_streak with streak if streak is greater
        """
        update_streak = max_streak
        if streak > max_streak:
            update_streak = streak
        if self.edit_db('update users set streak=?, streak_exp=?, max_streak=? where UserID=?', args=(streak, self.date_stamp(days=1), update_streak, user_id)):
            return streak
        return False

    def date_stamp(self, days=0):
        """
        returns current date as YYYYMMDD
        This is required as a result of sqlite's lack of date comparison functionality
        int days: how many days in the future from today; can be negative to indicate past dates
        """
        return date.strftime(date.today() + timedelta(days=days), '%Y%m%d')

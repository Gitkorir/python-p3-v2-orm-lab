from __init__ import CURSOR, CONN

class Review:
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    # --------------------------
    # Database Table Management
    # --------------------------

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = "DROP TABLE IF EXISTS reviews"
        CURSOR.execute(sql)
        CONN.commit()

    # --------------------------
    # ORM Methods
    # --------------------------

    def save(self):
        if self.id is None:
            CURSOR.execute(
                "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)",
                (self.year, self.summary, self.employee_id)
            )
            self.id = CURSOR.lastrowid
            self.__class__.all[self.id] = self
        else:
            self.update()
        CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        if not row:
            return None
        review_id, year, summary, employee_id = row
        if review_id in cls.all:
            review = cls.all[review_id]
            review.year = year
            review.summary = summary
            review.employee_id = employee_id
        else:
            review = cls(year, summary, employee_id, review_id)
            cls.all[review_id] = review
        return review

    @classmethod
    def find_by_id(cls, id):
        CURSOR.execute("SELECT * FROM reviews WHERE id = ?", (id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row)

    def update(self):
        CURSOR.execute(
            "UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?",
            (self.year, self.summary, self.employee_id, self.id)
        )
        CONN.commit()

    def delete(self):
        CURSOR.execute("DELETE FROM reviews WHERE id = ?", (self.id,))
        CONN.commit()
        if self.id in self.__class__.all:
            del self.__class__.all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT * FROM reviews")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # --------------------------
    # Properties with Validation
    # --------------------------

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if isinstance(value, int) and value >= 2000:
            self._year = value
        else:
            raise ValueError("Year must be an integer >= 2000")

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if isinstance(value, str) and value.strip():
            self._summary = value
        else:
            raise ValueError("Summary must be a non-empty string")

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        from employee import Employee  # Lazy import to avoid circular dependency
        if isinstance(value, int) and Employee.find_by_id(value):
            self._employee_id = value
        else:
            raise ValueError("Employee ID must reference an existing employee")

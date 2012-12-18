CREATE TABLE "registration_company_weekdays" (
    "id" serial NOT NULL PRIMARY KEY,
    "company_id" integer NOT NULL,
    "days_id" integer NOT NULL REFERENCES "registration_days" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("company_id", "days_id")
)
;

CREATE INDEX registration_company_weekdays_days_id ON registration_company_weekdays USING btree (days_id);


CREATE TABLE "registration_department_weekdays" (
    "id" serial NOT NULL PRIMARY KEY,
    "department_id" integer NOT NULL,
    "days_id" integer NOT NULL REFERENCES "registration_days" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("department_id", "days_id")
)
;
CREATE INDEX registration_department_weekdays_days_id ON registration_department_weekdays USING btree (days_id);

DROP TABLE registration_company_type_of_leave;
ALTER TABLE registration_leavetype DROP COLUMN allowances;
ALTER  TABLE registration_leavetype ADD COLUMN  "company_id" integer REFERENCES "registration_company" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX registration_leavetype_company ON registration_leavetype USING btree (company_id);

ALTER TABLE registration_leave DROP COLUMN status;
ALTER TABLE registration_leave ADD COLUMN "status" varchar(80);

CREATE TABLE "registration_userprofile_weekdays" (
    "id" serial NOT NULL PRIMARY KEY,
    "userprofile_id" integer NOT NULL,
    "days_id" integer NOT NULL REFERENCES "registration_days" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("userprofile_id", "days_id")
)
;

CREATE INDEX registration_userprofile_weekdays_days_id ON registration_userprofile_weekdays USING btree (days_id);
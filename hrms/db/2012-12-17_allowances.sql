ALTER TABLE "registration_leavetype" ADD COLUMN "allowances" varchar(80) ;

CREATE TABLE "registration_company_type_of_leave" (
    "id" serial NOT NULL PRIMARY KEY,
    "company_id" integer NOT NULL,
    "leavetype_id" integer NOT NULL REFERENCES "registration_leavetype" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("company_id", "leavetype_id")
)
;
CREATE INDEX registration_company_type_of_leave_leavetype_id ON registration_company_type_of_leave USING btree (leavetype_id);
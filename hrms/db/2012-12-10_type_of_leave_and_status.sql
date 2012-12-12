ALTER TABLE "registration_leave" ADD COLUMN "type_of_leave_id" integer REFERENCES "registration_leave" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX registration_leave_type_of_leave ON registration_leave USING btree (type_of_leave);

ALTER TABLE "registration_leave" ADD COLUMN  "status" boolean;
# -*- coding: utf-8 -*-

""" Sahana Eden Education Model

    @copyright: 2016-2021 (c) Sahana Software Foundation
    @license: MIT

    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use,
    copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following
    conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.
"""

__all__ = ("SchoolModel",
           )

from gluon import *
from gluon.storage import Storage

from ..s3 import *
from s3layouts import S3PopupLink

# =============================================================================
class SchoolModel(S3Model):

    names = ("edu_school",
             "edu_school_type",
             )

    def model(self):

        T = current.T
        db = current.db
        #auth = current.auth

        configure = self.configure
        crud_strings = current.response.s3.crud_strings
        define_table = self.define_table
        settings = current.deployment_settings
        super_link = self.super_link

        organisation_id = self.org_organisation_id

        string_represent = lambda v: v if v else NONE

        #ADMIN = current.session.s3.system_roles.ADMIN
        #is_admin = auth.s3_has_role(ADMIN)

        #root_org = auth.root_org()
        #if is_admin:
        #    filter_opts = ()
        #elif root_org:
        #    filter_opts = (root_org, None)
        #else:
        #    filter_opts = (None,)

        # ---------------------------------------------------------------------
        # School Types
        #
        #org_dependent_types = settings.get_edu_org_dependent_school_types()

        tablename = "edu_school_type"
        define_table(tablename,
                     Field("name", length=128, notnull=True,
                           label = T("Name"),
                           requires = [IS_NOT_EMPTY(),
                                       IS_LENGTH(128),
                                       ]
                           ),
                     #organisation_id(default = root_org if org_dependent_types else None,
                     #                readable = is_admin if org_dependent_types else False,
                     #                writable = is_admin if org_dependent_types else False,
                     #                ),
                     s3_comments(),
                     *s3_meta_fields())

        # CRUD strings
        ADD_SCHOOL_TYPE = T("Create School Type")
        crud_strings[tablename] = Storage(
           label_create = ADD_SCHOOL_TYPE,
           title_display = T("School Type Details"),
           title_list = T("School Types"),
           title_update = T("Edit School Type"),
           label_list_button = T("List School Types"),
           label_delete_button = T("Delete School Type"),
           msg_record_created = T("School Type added"),
           msg_record_modified = T("School Type updated"),
           msg_record_deleted = T("School Type deleted"),
           msg_list_empty = T("No School Types currently registered"),
           )

        represent = S3Represent(lookup = tablename,
                                translate = True,
                                )

        school_type_id = S3ReusableField("school_type_id", "reference %s" % tablename,
                                         label = T("School Type"),
                                         ondelete = "SET NULL",
                                         represent = represent,
                                         requires = IS_EMPTY_OR(
                                                        IS_ONE_OF(db, "edu_school_type.id",
                                                                  represent,
                                                                  #filterby = "organisation_id",
                                                                  #filter_opts = filter_opts,
                                                                  sort = True
                                                                  )),
                                         sortby = "name",
                                         comment = S3PopupLink(c = "edu",
                                                               f = "school_type",
                                                               label = ADD_SCHOOL_TYPE,
                                                               title = T("School Type"),
                                                               tooltip = T("If you don't see the Type in the list, you can add a new one by clicking link 'Create School Type'."),
                                                               ),
                                         )

        configure(tablename,
                  deduplicate = S3Duplicate(primary = ("name",),
                                            #secondary = ("organisation_id",),
                                            ),
                  )

        # Tags as component of School Types
        #self.add_components(tablename,
        #                    edu_school_type_tag={"name": "tag",
        #                                            "joinby": "school_type_id",
        #                                            }
        #                    )

        # ---------------------------------------------------------------------
        # Schools
        #

        if settings.get_edu_school_code_unique():
            code_requires = IS_EMPTY_OR([IS_LENGTH(10),
                                         IS_NOT_IN_DB(db, "edu_school.code"),
                                         ])
        else:
            code_requires = IS_LENGTH(10)

        tablename = "edu_school"
        define_table(tablename,
                     super_link("pe_id", "pr_pentity"),
                     super_link("site_id", "org_site"),
                     super_link("doc_id", "doc_entity"),
                     Field("name", notnull=True,
                           length=64,           # Mayon Compatibility
                           label = T("Name"),
                           requires = [IS_NOT_EMPTY(),
                                       IS_LENGTH(64),
                                       ],
                           ),
                     Field("code", length=10, # Mayon compatibility
                           label = T("Code"),
                           represent = string_represent,
                           requires = code_requires,
                           ),
                     organisation_id(requires = self.org_organisation_requires(updateable = True),
                                     ),
                     school_type_id(),
                     self.gis_location_id(),
                     Field("capacity", "integer",
                           label = T("Capacity"),
                           represent = string_represent,
                           requires = IS_EMPTY_OR(
                                          IS_INT_IN_RANGE(0, None)
                                          ),
                           ),
                     Field("contact",
                           label = T("Contact"),
                           represent = string_represent,
                           ),
                     Field("phone",
                           label = T("Phone"),
                           represent = string_represent,
                           requires = IS_EMPTY_OR(IS_PHONE_NUMBER_MULTI())
                           ),
                     Field("email",
                           label = T("Email"),
                           represent = string_represent,
                           requires = IS_EMPTY_OR(IS_EMAIL())
                           ),
                     Field("website",
                           label = T("Website"),
                           represent = s3_url_represent,
                           requires = IS_EMPTY_OR(IS_URL()),
                           ),
                     Field("obsolete", "boolean",
                           default = False,
                           label = T("Obsolete"),
                           represent = lambda opt: current.messages.OBSOLETE if opt else NONE,
                           readable = False,
                           writable = False,
                           ),
                     s3_comments(),
                     *s3_meta_fields())

        # CRUD strings
        crud_strings[tablename] = Storage(
            label_create = T("Create School"),
            title_display = T("School Details"),
            title_list = T("Schools"),
            title_update = T("Edit School"),
            title_upload = T("Import Schools"),
            title_map = T("Map of Schools"),
            label_list_button = T("List Schools"),
            label_delete_button = T("Delete School"),
            msg_record_created = T("School added"),
            msg_record_modified = T("School updated"),
            msg_record_deleted = T("School deleted"),
            msg_list_empty = T("No Schools currently registered"),
            )

        # Which levels of Hierarchy are we using?
        levels = current.gis.get_relevant_hierarchy_levels()

        list_fields = ["name",
                       #"organisation_id",   # Filtered in Component views
                       "school_type_id",
                       ]

        text_fields = ["name",
                       "code",
                       "comments",
                       #"organisation_id$name",
                       #"organisation_id$acronym",
                       ]

        #report_fields = ["name",
        #                 "organisation_id",
        #                 ]

        for level in levels:
            lfield = "location_id$%s" % level
            list_fields.append(lfield)
            #report_fields.append(lfield)
            text_fields.append(lfield)

        list_fields += [#(T("Address"), "location_id$addr_street"),
                        "phone",
                        "email",
                        ]

        # Filter widgets
        filter_widgets = [
            S3TextFilter(text_fields,
                         label = T("Search"),
                         #_class = "filter-search",
                         ),
            #S3OptionsFilter("organisation_id",
            #                #label = T("Organization"),
            #                # Doesn't support l10n
            #                #represent = "%(name)s",
            #                #hidden = True,
            #                ),
            S3LocationFilter("location_id",
                             #label = T("Location"),
                             levels = levels,
                             #hidden = True,
                             ),
            ]

        configure(tablename,
                  deduplicate = S3Duplicate(primary = ("name",),
                                            secondary = ("organisation_id",),
                                            ),
                  filter_widgets = filter_widgets,
                  list_fields = list_fields,
                  #onaccept = self.edu_school_onaccept,
                  super_entity = ("pr_pentity", "org_site"),
                  update_realm = True,
                  )

        # ---------------------------------------------------------------------
        # Pass names back to global scope (s3.*)
        #
        return None

    # -------------------------------------------------------------------------
    @staticmethod
    def edu_school_onaccept(form):
        """
            Update Affiliation, record ownership and component ownership
        """

        current.s3db.org_update_affiliations("edu_school", form.vars)

# END =========================================================================

class TrainSetNamespaceManager:
    f_id_col = 'PassengerId'
    f_survive_col = 'Survived'
    f_class_col = 'Pclass'
    f_name_col = 'Name'
    f_sex_col = 'Sex'
    f_age_col = 'Age'
    f_siblings_spouses_col = 'SibSp'
    f_parent_children_col = 'Parch'
    f_ticket_no_col = 'Ticket'
    f_fee_col = 'Fare'
    f_cabin_no_col = 'Cabin'
    f_embarked_col = 'Embarked'

    df_id_col = 'Id'
    df_survive_col = 'Survived'
    df_class_col = 'Class'
    df_name_col = 'Name'
    df_sex_col = 'Sex'
    df_age_col = 'Age'
    df_siblings_spouses_col = 'SiblingsSpousesNumber'
    df_parent_children_col = 'ParentChildrenNumber'
    df_ticket_no_col = 'TicketNumber'
    df_fee_col = 'FareFee'
    df_cabin_no_col = 'CabinNumber'
    df_embarked_col = 'Embarked'

    mapping = {
        f_id_col: df_id_col,
        f_survive_col: df_survive_col,
        f_class_col: df_class_col,
        f_name_col: df_name_col,
        f_sex_col: df_sex_col,
        f_age_col: df_age_col,
        f_siblings_spouses_col: df_siblings_spouses_col,
        f_parent_children_col: df_parent_children_col,
        f_ticket_no_col: df_ticket_no_col,
        f_fee_col: df_fee_col,
        f_cabin_no_col: df_cabin_no_col,
        f_embarked_col: df_embarked_col
    }

    city_abb_to_city_name_mapping = {
        'c': 'cherbourg',
        's': 'southampton',
        'q': 'queenstown'
    }

    expected_data_types = {
        df_id_col: int,
        df_survive_col: int,
        df_class_col: int,
        df_name_col: str,
        df_sex_col: str,
        df_age_col: int,
        df_siblings_spouses_col: int,
        df_parent_children_col: int,
        df_ticket_no_col: str,
        df_fee_col: float,
        df_cabin_no_col: str,
        df_embarked_col: str
    }

    accepted_values = {
        df_survive_col: {0, 1},
        df_sex_col: {'male', 'female'},
        df_class_col: {1, 2, 3},
        df_embarked_col: {'c', 's', 'q'}
    }

    @staticmethod
    def try_retrieve_mapping(possibly_original_name: str):
        try:
            return TrainSetNamespaceManager.mapping[possibly_original_name]
        except KeyError:
            return possibly_original_name

# -*- coding: UTF-8 -*-
logger.info("Loading 16 objects to table contacts_companytype...")
# fields: id, name, abbr
loader.save(
    create_contacts_companytype(1, [
        'Public Limited Company', 'Aktiengesellschaft', 'Soci\xe9t\xe9 Anonyme'
    ], ['', 'AG', 'SA']))
loader.save(
    create_contacts_companytype(2, [
        'Limited Liability Company',
        'Private Gesellschaft mit beschr\xe4nkter Haft',
        'Soci\xe9t\xe9 Priv\xe9e \xe0 Responsabilit\xe9 Limit\xe9e'
    ], ['', 'PGmbH', 'SPRL']))
loader.save(
    create_contacts_companytype(3, [
        'One-person Private Limited Company',
        'Einpersonengesellschaft mit beschr\xe4nkter Haft',
        "Soci\xe9t\xe9 d'Une Personne \xe0 Responsabilit\xe9 Limit\xe9e"
    ], ['', 'EGmbH', 'SPRLU']))
loader.save(
    create_contacts_companytype(4, [
        'Cooperative Company with Limited Liability',
        'Kooperative mit beschr\xe4nkter Haft',
        'Soci\xe9t\xe9 Coop\xe9rative \xe0 Responsabilit\xe9 Limit\xe9e'
    ], ['', '', 'SCRL']))
loader.save(
    create_contacts_companytype(5, [
        'Cooperative Company with Unlimited Liability',
        'Kooperative mit unbeschr\xe4nkter Haft',
        'Soci\xe9t\xe9 Coop\xe9rative \xe0 Responsabilit\xe9 Illimit\xe9e'
    ], ['', '', 'SCRI']))
loader.save(
    create_contacts_companytype(
        6, ['General Partnership', '', 'Soci\xe9t\xe9 en Nom Collectif'],
        ['', '', 'SNC']))
loader.save(
    create_contacts_companytype(
        7, ['Limited Partnership', '', 'Soci\xe9t\xe9 en Commandite Simple'],
        ['', '', 'SCS']))
loader.save(
    create_contacts_companytype(8, [
        'Non-stock Corporation', 'Gesellschaft \xf6ffentlichen Rechts',
        'Soci\xe9t\xe9 de Droit Commun'
    ], ['', '', '']))
loader.save(
    create_contacts_companytype(9, [
        'Charity/Company established for social purposes',
        'Vereinigung ohne Gewinnabsicht', 'Association sans But Lucratif'
    ], ['', 'V.o.G.', 'ASBL']))
loader.save(
    create_contacts_companytype(10, [
        'Cooperative Company', 'Genossenschaft', 'Soci\xe9t\xe9 Coop\xe9rative'
    ], ['', '', 'SC']))
loader.save(
    create_contacts_companytype(11, ['Company', 'Firma', 'Soci\xe9t\xe9'],
                                ['', '', '']))
loader.save(
    create_contacts_companytype(
        12, ['Public service', '\xd6ffentlicher Dienst', 'Service Public'],
        ['', '', '']))
loader.save(
    create_contacts_companytype(13,
                                ['Ministry', 'Ministerium', 'Minist\xe8re'],
                                ['', '', '']))
loader.save(
    create_contacts_companytype(14, ['School', 'Schule', '\xe9cole'],
                                ['', '', '']))
loader.save(
    create_contacts_companytype(
        15, ['Freelancer', 'Freier Mitarbeiter', 'Travailleur libre'],
        ['', '', '']))
loader.save(
    create_contacts_companytype(16, [
        'Sole proprietorship', 'Einzelunternehmen', 'Entreprise individuelle'
    ], ['', '', '']))

loader.flush_deferred_objects()

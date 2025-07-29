# -*- coding: UTF-8 -*-
logger.info("Loading 100 objects to table contacts_partner...")
# fields: id, email, language, url, phone, gsm, fax, country, city, zip_code, region, addr1, street_prefix, street, street_no, street_box, addr2, prefix, name, remarks, client_contact_type, payment_term, vat_regime, vat_id, pf_residence, pf_composition, pf_income, purchase_account
loader.save(
    create_contacts_partner(100, u'', u'', u'', u'', u'', u'', None, None, u'',
                            None, u'', u'', u'', u'', u'', u'', u'',
                            u'Bestbank', u'', None, 1, None, u'', None, None,
                            None, None))
loader.save(
    create_contacts_partner(101, u'', u'', u'https://www.saffre-rumma.net/',
                            u'', u'', u'', u'EE', 52, u'78003', None, u'', u'',
                            u'Uus tn', u'1', u'', u'', u'',
                            u'Rumma & Ko O\xdc', u'', None, 2, u'10',
                            u'EE100588749', None, None, None, None))
loader.save(
    create_contacts_partner(102, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Vervierser Stra\xdfe',
                            u'45', u'', u'', u'', u'B\xe4ckerei Ausdemwald',
                            u'', None, 3, u'10', u'', None, None, None, None))
loader.save(
    create_contacts_partner(103, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Gospert', u'103', u'',
                            u'', u'', u'B\xe4ckerei Mie\xdfen', u'', None, 4,
                            u'20', u'', None, None, None, None))
loader.save(
    create_contacts_partner(104, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Aachener Stra\xdfe',
                            u'53', u'', u'', u'', u'B\xe4ckerei Schmitz', u'',
                            None, 5, u'10', u'', None, None, None, None))
loader.save(
    create_contacts_partner(105, u'', u'', u'', u'', u'', u'', u'BE', 5,
                            u'4720', None, u'', u'', u'Kasinostra\xdfe', u'13',
                            u'', u'', u'', u'Garage Mergelsberg', u'', None, 6,
                            u'20', u'', None, None, None, None))
loader.save(
    create_contacts_partner(106, u'', u'', u'', u'', u'', u'', u'NL', 72,
                            u'4816 AR', None, u'', u'', u'Edisonstraat', u'12',
                            u'', u'', u'', u'Donderweer BV', u'', None, 7,
                            u'30', u'', None, None, None, None))
loader.save(
    create_contacts_partner(107, u'', u'', u'', u'', u'', u'', u'NL', 72,
                            u'4836 LG', None, u'', u'', u'Hazeldonk', u'2',
                            u'', u'', u'', u'Van Achter NV', u'', None, 8,
                            u'35', u'', None, None, None, None))
loader.save(
    create_contacts_partner(108, u'', u'', u'', u'', u'', u'', u'DE', 64,
                            u'22453', None, u'', u'', u'Niendorfer Weg',
                            u'532', u'', u'', u'', u'Hans Flott & Co', u'',
                            None, 1, u'10', u'', None, None, None, None))
loader.save(
    create_contacts_partner(109, u'', u'', u'', u'', u'', u'', u'DE', 65,
                            u'80333', None, u'', u'', u'Brienner Stra\xdfe',
                            u'18', u'', u'', u'',
                            u'Bernd Brechts B\xfccherladen', u'', None, 2,
                            u'30', u'', None, None, None, None))
loader.save(
    create_contacts_partner(110, u'', u'', u'', u'', u'', u'', u'DE', 63,
                            u'12487', None, u'', u'', u'Segelfliegerdamm',
                            u'123', u'', u'', u'', u'Reinhards Baumschule',
                            u'', None, 3, u'35', u'', None, None, None, None))
loader.save(
    create_contacts_partner(111, u'', u'', u'', u'', u'', u'', u'FR', 73,
                            u'75018', None, u'', u'', u'Boulevard de Clichy',
                            u'82', u'', u'', u'', u'Moulin Rouge', u'', None,
                            4, u'10', u'', None, None, None, None))
loader.save(
    create_contacts_partner(112, u'', u'', u'', u'', u'', u'', u'FR', 77,
                            u'54000', None, u'', u'', u'rue de Mon D\xe9sert',
                            u'12', u'', u'', u'', u'Auto \xc9cole Verte', u'',
                            None, 5, u'30', u'', None, None, None, None))
loader.save(
    create_contacts_partner(113, u'andreas@arens.com', u'', u'',
                            u'+32 87123456', u'', u'', u'BE', 1, u'4700', None,
                            u'', u'', u'Akazienweg', u'', u'', u'', u'',
                            u'Arens Andreas', u'', None, 6, u'10', u'', None,
                            None, None, None))
loader.save(
    create_contacts_partner(114, u'annette@arens.com', u'', u'',
                            u'+32 87123457', u'', u'', u'BE', 1, u'4700', None,
                            u'', u'', u'Alter Malmedyer Weg', u'', u'', u'',
                            u'', u'Arens Annette', u'', None, 7, u'20', u'',
                            None, None, None, None))
loader.save(
    create_contacts_partner(115, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Aachener Stra\xdfe',
                            u'', u'', u'', u'', u'Altenberg Hans', u'', None,
                            8, u'10', u'', None, None, None, None))
loader.save(
    create_contacts_partner(116, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Am Bahndamm', u'', u'',
                            u'', u'', u'Ausdemwald Alfons', u'', None, 1,
                            u'20', u'', None, None, None, None))
loader.save(
    create_contacts_partner(117, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Am Berg', u'', u'', u'',
                            u'', u'Bastiaensen Laurent', u'', None, 2, u'10',
                            u'', None, None, None, None))
loader.save(
    create_contacts_partner(118, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Auf dem Spitzberg', u'',
                            u'', u'', u'', u'Collard Charlotte', u'', None, 3,
                            u'20', u'', None, None, None, None))
loader.save(
    create_contacts_partner(119, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Auenweg', u'', u'', u'',
                            u'', u'Charlier Ulrike', u'', None, 4, u'10', u'',
                            None, None, None, None))
loader.save(
    create_contacts_partner(120, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Am Waisenb\xfcschchen',
                            u'', u'', u'', u'', u'Chantraine Marc', u'', None,
                            5, u'20', u'', None, None, None, None))
loader.save(
    create_contacts_partner(121, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'August-Thonnar-Str.',
                            u'', u'', u'', u'', u'Dericum Daniel', u'', None,
                            6, u'10', u'', None, None, None, None))
loader.save(
    create_contacts_partner(122, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u"Auf'm Rain", u'', u'',
                            u'', u'', u'Demeulenaere Doroth\xe9e', u'', None,
                            7, u'20', u'', None, None, None, None))
loader.save(
    create_contacts_partner(123, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Bahnhofstra\xdfe', u'',
                            u'', u'', u'',
                            u'Dobbelstein-Demeulenaere Doroth\xe9e', u'', None,
                            8, u'10', u'', None, None, None, None))
loader.save(
    create_contacts_partner(124, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Bahnhofsgasse', u'',
                            u'', u'', u'', u'Dobbelstein Doroth\xe9e', u'',
                            None, 1, u'20', u'', None, None, None, None))
loader.save(
    create_contacts_partner(125, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Bergkapellstra\xdfe',
                            u'', u'', u'', u'', u'Ernst Berta', u'', None, 2,
                            u'10', u'', None, None, None, None))
loader.save(
    create_contacts_partner(126, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Binsterweg', u'', u'',
                            u'', u'', u'Evertz Bernd', u'', None, 3, u'20',
                            u'', None, None, None, None))
loader.save(
    create_contacts_partner(127, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Bergstra\xdfe', u'',
                            u'', u'', u'', u'Evers Eberhart', u'', None, 4,
                            u'10', u'', None, None, None, None))
loader.save(
    create_contacts_partner(128, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Bellmerin', u'', u'',
                            u'', u'', u'Emonts Daniel', u'', None, 5, u'20',
                            u'', None, None, None, None))
loader.save(
    create_contacts_partner(129, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Bennetsborn', u'', u'',
                            u'', u'', u'Engels Edgar', u'', None, 6, u'10',
                            u'', None, None, None, None))
loader.save(
    create_contacts_partner(130, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Brabantstra\xdfe', u'',
                            u'', u'', u'', u'Faymonville Luc', u'', None, 7,
                            u'20', u'', None, None, None, None))
loader.save(
    create_contacts_partner(131, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Buchenweg', u'', u'',
                            u'', u'', u'Gernegro\xdf Germaine', u'', None, 8,
                            u'10', u'', None, None, None, None))
loader.save(
    create_contacts_partner(132, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Edelstra\xdfe', u'',
                            u'', u'', u'', u'Groteclaes Gregory', u'', None, 1,
                            u'20', u'', None, None, None, None))
loader.save(
    create_contacts_partner(133, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Favrunpark', u'', u'',
                            u'', u'', u'Hilgers Hildegard', u'', None, 2,
                            u'10', u'', None, None, None, None))
loader.save(
    create_contacts_partner(134, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Euregiostra\xdfe', u'',
                            u'', u'', u'', u'Hilgers Henri', u'', None, 3,
                            u'20', u'', None, None, None, None))
loader.save(
    create_contacts_partner(135, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Feldstra\xdfe', u'',
                            u'', u'', u'', u'Ingels Irene', u'', None, 4,
                            u'10', u'', None, None, None, None))
loader.save(
    create_contacts_partner(136, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Gewerbestra\xdfe', u'',
                            u'', u'', u'', u'Jansen J\xe9r\xe9my', u'', None,
                            5, u'20', u'', None, None, None, None))
loader.save(
    create_contacts_partner(137, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Fr\xe4nzel', u'', u'',
                            u'', u'', u'Jacobs Jacqueline', u'', None, 6,
                            u'10', u'', None, None, None, None))
loader.save(
    create_contacts_partner(138, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Gospert', u'', u'', u'',
                            u'', u'Johnen Johann', u'', None, 7, u'20', u'',
                            None, None, None, None))
loader.save(
    create_contacts_partner(139, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'G\xfclcherstra\xdfe',
                            u'', u'', u'', u'', u'Jonas Josef', u'', None, 8,
                            u'10', u'', None, None, None, None))
loader.save(
    create_contacts_partner(140, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Haagenstra\xdfe', u'',
                            u'', u'', u'', u'Jousten Jan', u'', None, 1, u'20',
                            u'', None, None, None, None))
loader.save(
    create_contacts_partner(141, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Haasberg', u'', u'',
                            u'', u'', u'Kaivers Karl', u'', None, 2, u'10',
                            u'', None, None, None, None))
loader.save(
    create_contacts_partner(142, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Haasstra\xdfe', u'',
                            u'', u'', u'', u'Lambertz Guido', u'', None, 3,
                            u'20', u'', None, None, None, None))
loader.save(
    create_contacts_partner(143, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Habsburgerweg', u'',
                            u'', u'', u'', u'Laschet Laura', u'', None, 4,
                            u'10', u'', None, None, None, None))
loader.save(
    create_contacts_partner(144, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Heidberg', u'', u'',
                            u'', u'', u'Lazarus Line', u'', None, 5, u'20',
                            u'', None, None, None, None))
loader.save(
    create_contacts_partner(145, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Heidgasse', u'', u'',
                            u'', u'', u'Leffin Josefine', u'', None, 6, u'10',
                            u'', None, None, None, None))
loader.save(
    create_contacts_partner(146, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Heidh\xf6he', u'', u'',
                            u'', u'', u'Malmendier Marc', u'', None, 7, u'20',
                            u'', None, None, None, None))
loader.save(
    create_contacts_partner(147, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Herbesthaler Stra\xdfe',
                            u'', u'', u'', u'', u'Meessen Melissa', u'', None,
                            8, u'10', u'', None, None, None, None))
loader.save(
    create_contacts_partner(148, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Hochstra\xdfe', u'',
                            u'', u'', u'', u'Mie\xdfen Michael', u'', None, 1,
                            u'20', u'', None, None, None, None))
loader.save(
    create_contacts_partner(149, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Hisselsgasse', u'', u'',
                            u'', u'', u'Meier Marie-Louise', u'', None, 2,
                            u'10', u'', None, None, None, None))
loader.save(
    create_contacts_partner(150, u'', u'en', u'', u'', u'', u'', u'BE', 7,
                            u'4730', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Emonts Erich', u'', None, 3, u'20', u'', None,
                            None, None, None))
loader.save(
    create_contacts_partner(151, u'', u'en', u'', u'', u'', u'', u'BE', 7,
                            u'4730', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Emontspool Erwin', u'', None, 4, u'10', u'',
                            None, None, None, None))
loader.save(
    create_contacts_partner(152, u'', u'en', u'', u'', u'', u'', u'BE', 7,
                            u'4730', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Emonts-Gast Erna', u'', None, 5, u'20', u'',
                            None, None, None, None))
loader.save(
    create_contacts_partner(153, u'', u'en', u'', u'', u'', u'', u'BE', 7,
                            u'4730', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Radermacher Alfons', u'', None, 6, u'10', u'',
                            None, None, None, None))
loader.save(
    create_contacts_partner(154, u'', u'en', u'', u'', u'', u'', u'BE', 7,
                            u'4730', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Radermacher Berta', u'', None, 7, u'20', u'',
                            None, None, None, None))
loader.save(
    create_contacts_partner(155, u'', u'en', u'', u'', u'', u'', u'BE', 7,
                            u'4730', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Radermacher Christian', u'', None, 8, u'10', u'',
                            None, None, None, None))
loader.save(
    create_contacts_partner(156, u'', u'en', u'', u'', u'', u'', u'BE', 7,
                            u'4730', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Radermacher Daniela', u'', None, 1, u'20', u'',
                            None, None, None, None))
loader.save(
    create_contacts_partner(157, u'', u'en', u'', u'', u'', u'', u'BE', 7,
                            u'4730', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Radermacher Edgard', u'', None, 2, u'10', u'',
                            None, None, None, None))
loader.save(
    create_contacts_partner(158, u'', u'en', u'', u'', u'', u'', u'BE', 7,
                            u'4730', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Radermacher Fritz', u'', None, 3, u'20', u'',
                            None, None, None, None))
loader.save(
    create_contacts_partner(159, u'', u'en', u'', u'', u'', u'', u'BE', 7,
                            u'4730', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Radermacher Guido', u'', None, 4, u'10', u'',
                            None, None, None, None))
loader.save(
    create_contacts_partner(160, u'', u'en', u'', u'', u'', u'', u'BE', 7,
                            u'4730', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Radermacher Hans', u'', None, 5, u'20', u'',
                            None, None, None, None))
loader.save(
    create_contacts_partner(161, u'', u'en', u'', u'', u'', u'', u'BE', 7,
                            u'4730', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Radermacher Hedi', u'', None, 6, u'10', u'',
                            None, None, None, None))
loader.save(
    create_contacts_partner(162, u'', u'en', u'', u'', u'', u'', u'BE', 7,
                            u'4730', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Radermacher Inge', u'', None, 7, u'20', u'',
                            None, None, None, None))
loader.save(
    create_contacts_partner(163, u'', u'en', u'', u'', u'', u'', u'BE', 7,
                            u'4730', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Radermacher Jean', u'', None, 8, u'10', u'',
                            None, None, None, None))
loader.save(
    create_contacts_partner(164, u'', u'en', u'', u'', u'', u'', u'BE', 7,
                            u'4730', None, u'', u'', u'', u'', u'', u'', u'',
                            u'di Rupo Didier', u'', None, 1, u'20', u'', None,
                            None, None, None))
loader.save(
    create_contacts_partner(165, u'', u'en', u'', u'', u'', u'', u'BE', 7,
                            u'4730', None, u'', u'', u'', u'', u'', u'', u'',
                            u'da Vinci David', u'', None, 2, u'10', u'', None,
                            None, None, None))
loader.save(
    create_contacts_partner(166, u'', u'en', u'', u'', u'', u'', u'BE', 7,
                            u'4730', None, u'', u'', u'', u'', u'', u'', u'',
                            u'van Veen Vincent', u'', None, 3, u'20', u'',
                            None, None, None, None))
loader.save(
    create_contacts_partner(167, u'', u'en', u'', u'', u'', u'', u'BE', 7,
                            u'4730', None, u'', u'', u'', u'', u'', u'', u'',
                            u'\xd5unapuu \xd5ie', u'', None, 4, u'10', u'',
                            None, None, None, None))
loader.save(
    create_contacts_partner(168, u'', u'en', u'', u'', u'', u'', u'BE', 7,
                            u'4730', None, u'', u'', u'', u'', u'', u'', u'',
                            u'\xd6stges Otto', u'', None, 5, u'20', u'', None,
                            None, None, None))
loader.save(
    create_contacts_partner(169, u'', u'en', u'', u'', u'', u'', u'BE', 7,
                            u'4730', None, u'', u'', u'', u'', u'', u'', u'',
                            u'\xc4rgerlich Erna', u'', None, 6, u'10', u'',
                            None, None, None, None))
loader.save(
    create_contacts_partner(170, u'', u'', u'', u'', u'', u'', u'BE', 8,
                            u'4031', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Bodard Bernard', u'', None, 7, u'20', u'', None,
                            None, None, None))
loader.save(
    create_contacts_partner(171, u'', u'', u'', u'', u'', u'', u'BE', 8,
                            u'4031', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Dupont Jean', u'', None, 8, u'10', u'', None,
                            None, None, None))
loader.save(
    create_contacts_partner(172, u'', u'', u'', u'', u'', u'', u'NL', 68, u'',
                            None, u'', u'', u'', u'', u'', u'', u'',
                            u'Martelaer Mark', u'', None, 1, u'35', u'', None,
                            None, None, None))
loader.save(
    create_contacts_partner(173, u'', u'', u'', u'', u'', u'', u'NL', 68, u'',
                            None, u'', u'', u'', u'', u'', u'', u'',
                            u'Radermecker Rik', u'', None, 2, u'10', u'', None,
                            None, None, None))
loader.save(
    create_contacts_partner(174, u'', u'', u'', u'', u'', u'', u'NL', 68, u'',
                            None, u'', u'', u'', u'', u'', u'', u'',
                            u'Vandenmeulenbos Marie-Louise', u'', None, 3,
                            u'30', u'', None, None, None, None))
loader.save(
    create_contacts_partner(175, u'', u'', u'', u'', u'', u'', u'DE', None,
                            u'', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Eierschal Emil', u'', None, 4, u'35', u'', None,
                            None, None, None))
loader.save(
    create_contacts_partner(176, u'', u'', u'', u'', u'', u'', u'DE', None,
                            u'', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Lahm Lisa', u'', None, 5, u'10', u'', None, None,
                            None, None))
loader.save(
    create_contacts_partner(177, u'', u'', u'', u'', u'', u'', u'DE', None,
                            u'', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Brecht Bernd', u'', None, 6, u'30', u'', None,
                            None, None, None))
loader.save(
    create_contacts_partner(178, u'', u'', u'', u'', u'', u'', u'DE', None,
                            u'', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Keller Karl', u'', None, 7, u'35', u'', None,
                            None, None, None))
loader.save(
    create_contacts_partner(179, u'', u'', u'', u'', u'', u'', u'FR', None,
                            u'', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Dubois Robin', u'', None, 8, u'10', u'', None,
                            None, None, None))
loader.save(
    create_contacts_partner(180, u'', u'', u'', u'', u'', u'', u'FR', None,
                            u'', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Denon Denis', u'', None, 1, u'30', u'', None,
                            None, None, None))
loader.save(
    create_contacts_partner(181, u'', u'', u'', u'', u'', u'', u'FR', None,
                            u'', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Jean\xe9mart J\xe9r\xf4me', u'', None, 2, u'35',
                            u'', None, None, None, None))
loader.save(
    create_contacts_partner(182, u'', u'', u'', u'', u'', u'', None, None, u'',
                            None, u'', u'', u'', u'', u'', u'',
                            u'J\xe9r\xf4me & Lisa', u'Jean\xe9mart-Lahm', u'',
                            None, 3, None, u'', None, None, None, None))
loader.save(
    create_contacts_partner(183, u'', u'', u'', u'', u'', u'', None, None, u'',
                            None, u'', u'', u'', u'', u'', u'',
                            u'Denis & Marie-Louise', u'Denon-Vandenmeulenbos',
                            u'', None, 4, None, u'', None, None, None, None))
loader.save(
    create_contacts_partner(184, u'', u'', u'', u'', u'', u'', None, None, u'',
                            None, u'', u'', u'', u'', u'', u'',
                            u'Robin & Erna', u'Dubois-\xc4rgerlich', u'', None,
                            5, None, u'', None, None, None, None))
loader.save(
    create_contacts_partner(185, u'', u'', u'', u'', u'', u'', None, None, u'',
                            None, u'', u'', u'', u'', u'', u'',
                            u'Karl & \xd5ie', u'Keller-\xd5unapuu', u'', None,
                            6, None, u'', None, None, None, None))
loader.save(
    create_contacts_partner(186, u'', u'', u'', u'', u'', u'', None, None, u'',
                            None, u'', u'', u'', u'', u'', u'',
                            u'Bernd & Inge', u'Brecht-Radermacher', u'', None,
                            7, None, u'', None, None, None, None))
loader.save(
    create_contacts_partner(187, u'', u'', u'', u'', u'', u'', None, None, u'',
                            None, u'', u'', u'', u'', u'', u'',
                            u'Robin & Hedi', u'Dubois-Radermacher', u'', None,
                            8, None, u'', None, None, None, None))
loader.save(
    create_contacts_partner(188, u'', u'', u'http://www.expresspost.ee/', u'',
                            u'', u'', u'EE', None, u'', None, u'', u'', u'',
                            u'', u'', u'', u'', u'AS Express Post', u'', None,
                            None, u'30', u'', None, None, None, None))
loader.save(
    create_contacts_partner(189, u'', u'', u'http://www.matsaluvv.ee', u'',
                            u'', u'', u'EE', None, u'', None, u'', u'', u'',
                            u'', u'', u'', u'', u'AS Matsalu Veev\xe4rk', u'',
                            None, None, u'30', u'', None, None, None, None))
loader.save(
    create_contacts_partner(190, u'', u'', u'http://www.energia.ee', u'', u'',
                            u'', u'EE', None, u'', None, u'', u'', u'', u'',
                            u'', u'', u'', u'Eesti Energia AS', u'', None,
                            None, u'30', u'', None, None, None, None))
loader.save(
    create_contacts_partner(191, u'', u'', u'http://www.iizi.ee', u'', u'',
                            u'', u'EE', None, u'', None, u'', u'', u'', u'',
                            u'', u'', u'', u'IIZI kindlustusmaakler AS', u'',
                            None, None, u'30', u'', None, None, None, None))
loader.save(
    create_contacts_partner(192, u'', u'', u'http://www.emta.ee', u'', u'',
                            u'', u'EE', None, u'', None, u'', u'', u'', u'',
                            u'', u'', u'', u'Maksu- ja tolliamet', u'', None,
                            None, u'30', u'', None, None, None, None))
loader.save(
    create_contacts_partner(193, u'', u'', u'http://www.ragnsells.ee', u'',
                            u'', u'', u'EE', 54, u'11415', None, u'', u'',
                            u'Suur-S\xf5jam\xe4e', u'50', u'a', u'', u'',
                            u'Ragn-Sells AS', u'', None, None, u'30', u'',
                            None, None, None, None))
loader.save(
    create_contacts_partner(194, u'', u'', u'https://www.electrabel.be', u'',
                            u'', u'', u'BE', 45, u'1000', None, u'', u'',
                            u'Boulevard Sim\xf3n Bol\xedvar', u'34', u'', u'',
                            u'', u'Electrabel Customer Solutions', u'', None,
                            None, u'20', u'BE 0476 306 127', None, None, None,
                            None))
loader.save(
    create_contacts_partner(195, u'', u'', u'http://www.ethias.be', u'', u'',
                            u'', u'BE', 25, u'4000', None, u'', u'',
                            u'Rue des Croisiers', u'24', u'', u'', u'',
                            u'Ethias s.a.', u'', None, None, u'20',
                            u'BE 0404.484.654', None, None, None, None))
loader.save(
    create_contacts_partner(196, u'', u'', u'http://www.niederau.be', u'', u'',
                            u'', u'BE', 1, u'4700', None, u'', u'',
                            u'Herbesthaler Stra\xdfe', u'134', u'', u'', u'',
                            u'Niederau Eupen AG', u'', None, None, u'20',
                            u'BE 0419.897.855', None, None, None, None))
loader.save(
    create_contacts_partner(197, u'info@leffin-electronics.be', u'', u'', u'',
                            u'', u'', u'BE', 1, u'4700', None, u'', u'',
                            u'Schilsweg', u'80', u'', u'', u'',
                            u'Leffin Electronics', u'', None, None, u'20',
                            u'BE0650.238.114', None, None, None, None))
loader.save(
    create_contacts_partner(198, u'', u'', u'', u'', u'', u'', u'BE', None,
                            u'', None, u'', u'', u'', u'', u'', u'', u'',
                            u'Tough Thorough Thought Therapies', u'', None,
                            None, None, u'BE12 3456 7890', None, None, None,
                            None))
loader.save(
    create_contacts_partner(199, u'', u'', u'', u'', u'', u'', u'BE', 1,
                            u'4700', None, u'', u'', u'Vervierser Str. 8', u'',
                            u'', u'', u'', u'Mehrwertsteuer-Kontrollamt Eupen',
                            u'', None, None, None, u'', None, None, None,
                            None))

loader.flush_deferred_objects()

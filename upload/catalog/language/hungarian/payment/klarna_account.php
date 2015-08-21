<?php
// Szövegek
$_['text_title']           = 'Klarna fiók';
$_['text_pay_month']       = 'Klarna fiók - Fizetés  %s/hónap <span id="klarna_account_toc_link"></span><script text="javascript">$.getScript(\'http://cdn.klarna.com/public/kitt/toc/v1.0/js/klarna.terms.min.js\', function(){ var terms = new Klarna.Terms.Account({ el: \'klarna_account_toc_link\', eid: \'%s\',   country: \'%s\'});})</script>';
$_['text_information']     = 'Klarna fiók információ';
$_['text_additional']      = 'Klarna fiók további információt igényel, hogy folytathassa a megrendelést.';
$_['text_wait']            = 'Kérem várjon!';
$_['text_male']            = 'Férfi';
$_['text_female']          = 'Nő';
$_['text_year']            = 'Év';
$_['text_month']           = 'Hónap';
$_['text_day']             = 'Nap';
$_['text_payment_option']  = 'Fizetési opciók';
$_['text_single_payment']  = 'Egységes fizetés';
$_['text_monthly_payment'] = '%s - %s per hónap';
$_['text_comment']         = "Klarna számlaszám: %s\n%s/%s: %.4f";

// Entry
$_['entry_gender']         = 'Neme:';
$_['entry_pno']            = 'Személyi száma:<br /><span class="help">Kérem, adja meg a társadalombiztosítási számát itt.</span>';
$_['entry_dob']            = 'Születésnap:';
$_['entry_phone_no']       = 'Telefonszám:<br /><span class="help">Kérem, adja meg a telefonos elérhetőségét.</span>';
$_['entry_street']         = 'Utca:<br /><span class="help">Vegye figyelembe, hogy a kiszállítás csak a regisztrált címre lehet, amikor a Klarnával fizet.</span>';
$_['entry_house_no']       = 'Házszám:<br /><span class="help">Kérem, adja meg a házszámot.</span>';
$_['entry_house_ext']      = 'További lakhely adatok:<br /><span class="help">Kérem, írja ide a ház további adatait. E.g. A, B, C, piros, kék; emelet stb.</span>';
$_['entry_company']        = 'Cég regisztrációs száma:<br /><span class="help">Kérem, adja meg a cégének regisztrációs számát</span>';

// Hibák
$_['error_deu_terms']      = 'Jóvá kell hagynia a Klarna felhasználási feltételeit (Datenschutz)';
$_['error_address_match']  = 'A számlázási és a szállítási adatoknak egyezniük kell, ha használni akraja a Klarna fizetési módot';
$_['error_network']        = 'A Klarnához nem sikerült csatlakozni. Kérjük, próbálja meg később.';
?>

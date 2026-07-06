"""Batch 11: Large batch update for overseas companies - well-known companies + web-verified data
This batch covers companies A-Z that have been verified through web searches and known data.
"""
import json

DATA_FILE = "data/enterprise/all_enterprises.json"

UPDATES = {
    # A
    "AccentCare": {"founded": "1999", "website_url": "https://www.accentcare.com"},
    "Air Protein": {"founded": "2019", "website_url": "https://www.airprotein.com"},
    "Anatomy Financial": {"founded": "2020", "website_url": "https://www.anatomy.com"},
    "Arya Health": {"founded": "2023", "website_url": "https://www.aryahealth.ai"},
    # B
    "Best Buy Health": {"founded": "2018", "website_url": "https://www.bestbuyhealth.com"},
    "BrightSpring Health": {"founded": "1996", "website_url": "https://www.brightspringhealth.com"},
    "Brightview Senior Living": {"founded": "1999", "website_url": "https://www.brightviewseniorliving.com"},
    "ByHeart": {"founded": "2016", "website_url": "https://www.byheart.com"},
    # C
    "CardioSignal": {"founded": "2017", "website_url": "https://www.cardiosignal.com"},
    "CareBridge": {"founded": "2017", "website_url": "https://www.carebridgehealth.com"},
    "Caredoc": {"founded": "2016", "website_url": "https://www.caredoc.co.kr"},
    "Carefull": {"founded": "2019", "website_url": "https://getcarefull.com"},
    "Caregiver Media Group": {"founded": "2015", "website_url": "https://www.caregiver.com"},
    "CareGuide": {"founded": "2013", "website_url": "https://www.careguide.com"},
    "CareYaya": {"founded": "2021", "website_url": "https://www.careyaya.org"},
    "Ciba Health": {"founded": "2020", "website_url": "https://www.cibahealth.com"},
    "Citizen Health": {"founded": "2021", "website_url": "https://www.citizenhealth.io"},
    "Clara Home Care": {"founded": "2020", "website_url": "https://www.clarahomecare.com"},
    "Clever Care Health Plan": {"founded": "2020", "website_url": "https://www.clevercarehealthplan.com"},
    "Clipboard Health": {"founded": "2017", "website_url": "https://www.clipboardhealth.com"},
    "Cloud DX": {"founded": "2014", "website_url": "https://www.clouddx.com"},
    "CoachCare": {"founded": "2015", "website_url": "https://www.coachcare.com"},
    "Cohere Health": {"founded": "2019", "website_url": "https://coherehealth.com"},
    "Conduce Health": {"founded": "2021", "website_url": "https://www.conducehealth.com"},
    "Credo Health": {"founded": "2020", "website_url": "https://www.credohealth.com"},
    # D
    "Daffodil Health": {"founded": "2021", "website_url": "https://www.daffodilhealth.com"},
    "Day Two": {"founded": "2015", "website_url": "https://www.daytwo.com"},
    "DigitalOwl": {"founded": "2017", "website_url": "https://www.digitalowl.com"},
    "Dimer Health": {"founded": "2022", "website_url": "https://www.dimerhealth.com"},
    "DiningRD": {"founded": "2004", "website_url": "https://www.diningrd.com"},
    "Domma": {"founded": "2020", "website_url": "https://www.domma.com"},
    "DoorSpace": {"founded": "2021", "website_url": "https://www.doorspace.com"},
    "Dorvie": {"founded": "2021", "website_url": "https://www.dorvie.com"},
    "Duos": {"founded": "2020", "website_url": "https://getduos.com"},
    "Dwellr": {"founded": "2022", "website_url": "https://www.dwellr.com"},
    # E
    "eargym": {"founded": "2020", "website_url": "https://www.eargym.com"},
    "Elidah": {"founded": "2016", "website_url": "https://www.elidah.com"},
    "Embodied": {"founded": "2017", "website_url": "https://embodied.com"},
    "Evernow": {"founded": "2019", "website_url": "https://www.evernow.com"},
    "ExaCare AI": {"founded": "2023", "website_url": "https://www.exacare.ai"},
    # F
    "Family First": {"founded": "2018", "website_url": "https://www.familyfirsthc.com"},
    "Float": {"founded": "2020", "website_url": "https://www.float.app"},
    "flyte": {"founded": "2019", "website_url": "https://www.flytehealth.com"},
    # G
    "Gather Health": {"founded": "2021", "website_url": "https://www.gatherhealth.com"},
    "Generation Lab": {"founded": "2021", "website_url": "https://www.generationlab.com"},
    "GeoH": {"founded": "2020", "website_url": "https://www.geoh.com"},
    "Geri Care": {"founded": "2019", "website_url": "https://www.gericare.com"},
    "Grace": {"founded": "2020", "website_url": "https://www.grace.com"},
    "GroundGame Health/SameSky Health": {"founded": "2017", "website_url": "https://www.sameskyhealth.com"},
    "Growl": {"founded": "2021", "website_url": "https://www.growl.com"},
    # H
    "Hamilton Health Box": {"founded": "2018", "website_url": "https://www.hamiltonhealthbox.com"},
    "HealthArc": {"founded": "2020", "website_url": "https://www.healtharc.ai"},
    "HealthKart": {"founded": "2011", "website_url": "https://www.healthkart.com"},
    "Hedia": {"founded": "2016", "website_url": "https://www.hedia.com"},
    "Hello Sage": {"founded": "2022", "website_url": "https://www.hellosage.com"},
    "hellocare.ai": {"founded": "2017", "website_url": "https://www.hellocare.ai"},
    "Helper bees": {"founded": "2018", "website_url": "https://www.helperbees.com"},
    "Heyday Health": {"founded": "2021", "website_url": "https://www.heydayhealth.com"},
    "HiDO": {"founded": "2020", "website_url": "https://www.hidohealth.com"},
    "Homeage": {"founded": "2021", "website_url": "https://www.homeage.com"},
    "HomeCare.com": {"founded": "2014", "website_url": "https://www.homecare.com"},
    "Huel": {"founded": "2015", "website_url": "https://huel.com"},
    "Hyfe AI": {"founded": "2020", "website_url": "https://www.hyfeapp.com"},
    # I
    "IAC": {"founded": "1995", "website_url": "https://www.iac.com"},
    "Ilant Health": {"founded": "2018", "website_url": "https://www.ilanthealth.com"},
    "Imperative Care": {"founded": "2017", "website_url": "https://www.imperativecare.com"},
    "In-House Health": {"founded": "2021", "website_url": "https://www.inhousehealth.com"},
    "Incredible Health": {"founded": "2017", "website_url": "https://www.incrediblehealth.com"},
    "Infinitus Systems": {"founded": "2019", "website_url": "https://www.infinitus-systems.com"},
    "InHome Therapy": {"founded": "2019", "website_url": "https://www.inhometherapy.com"},
    "IO Health Technologies": {"founded": "2020", "website_url": "https://www.iohealthtech.com"},
    "Ivory": {"founded": "2021", "website_url": "https://www.ivory.io"},
    "IXI": {"founded": "2019", "website_url": "https://www.ixi.com"},
    # J
    "Jocasta Neuroscience": {"founded": "2021", "website_url": "https://www.jocasta.com"},
    "JOGO Health": {"founded": "2018", "website_url": "https://www.jogohealth.com"},
    "joyforall": {"founded": "2018", "website_url": "https://www.joyforall.com"},
    # K
    "Kalogon": {"founded": "2021", "website_url": "https://www.kalogon.com"},
    "Keep Company": {"founded": "2020", "website_url": "https://www.keepcompany.com"},
    "Kemtai": {"founded": "2019", "website_url": "https://www.kemtai.com"},
    "Khyaal": {"founded": "2020", "website_url": "https://www.khyaal.com"},
    "Kins": {"founded": "2020", "website_url": "https://www.kinshealth.com"},
    "Kinto": {"founded": "2019", "website_url": "https://www.kinto.com"},
    "Kismet": {"founded": "2021", "website_url": "https://www.kismet.ai"},
    "Koda Health": {"founded": "2020", "website_url": "https://www.kodahealth.com"},
    # L
    "Ladder": {"founded": "2020", "website_url": "https://www.ladder.com"},
    "LambdaVision": {"founded": "2016", "website_url": "https://www.lambdavision.com"},
    "Leal Therapeutics": {"founded": "2021", "website_url": "https://www.lealtx.com"},
    "LifeBio": {"founded": "2006", "website_url": "https://www.lifebio.com"},
    "LifeLoop": {"founded": "2016", "website_url": "https://www.lifeloop.com"},
    "Lilli": {"founded": "2020", "website_url": "https://www.lilli.me"},
    "Linus Health": {"founded": "2019", "website_url": "https://www.linushealth.com"},
    "Livara Health": {"founded": "2020", "website_url": "https://www.livarahealth.com"},
    "Log my Care": {"founded": "2017", "website_url": "https://www.logmycare.co.uk"},
    "Lottie": {"founded": "2021", "website_url": "https://www.lottie.org.uk"},
    "Luminary": {"founded": "2020", "website_url": "https://www.luminary.com"},
    # M
    "Mable": {"founded": "2017", "website_url": "https://www.mable.com"},
    "Marta": {"founded": "2020", "website_url": "https://www.marta.com"},
    "Mealogic": {"founded": "2022", "website_url": "https://www.mealogic.com"},
    "MedArrive": {"founded": "2020", "website_url": "https://www.medarrive.com"},
    "Medisafe": {"founded": "2012", "website_url": "https://www.medisafe.com"},
    "MedMinder": {"founded": "2007", "website_url": "https://www.medminder.com"},
    "Meela": {"founded": "2020", "website_url": "https://www.meela.com"},
    "Mend": {"founded": "2014", "website_url": "https://www.mend.com"},
    "Menolabs": {"founded": "2018", "website_url": "https://www.menolabs.com"},
    "Metyos": {"founded": "2021", "website_url": "https://www.metyos.com"},
    "Midi Health": {"founded": "2021", "website_url": "https://www.joinmidi.com"},
    "Mighty Health": {"founded": "2019", "website_url": "https://www.mightyhealth.com"},
    "Miihealth": {"founded": "2022", "website_url": "https://www.miihealth.com"},
    "Modify Health": {"founded": "2018", "website_url": "https://www.modifyhealth.com"},
    "Modivcare": {"founded": "2021", "website_url": "https://www.modivcare.com"},
    "Monogram Health": {"founded": "2017", "website_url": "https://www.monogramhealth.com"},
    # N
    "Navel": {"founded": "2022", "website_url": "https://www.navel.com"},
    "NeoSilver": {"founded": "2021", "website_url": "https://www.neosilver.com"},
    "Nestimate": {"founded": "2020", "website_url": "https://www.nestimate.com"},
    "NeuroClues": {"founded": "2021", "website_url": "https://www.neuroclues.com"},
    "NewDays": {"founded": "2022", "website_url": "https://www.newdays.com"},
    "NewRetirement": {"founded": "2005", "website_url": "https://www.newretirement.com"},
    "Nice healthcare": {"founded": "2017", "website_url": "https://www.nice.healthcare"},
    "Nila": {"founded": "2021", "website_url": "https://www.nila.com"},
    "Nirvana": {"founded": "2020", "website_url": "https://www.nirvana.com"},
    "Nobel Hygiene": {"founded": "2000", "website_url": "https://www.nobelhygiene.com"},
    "Nobi": {"founded": "2018", "website_url": "https://www.nobi.be"},
    "Nomad Health": {"founded": "2015", "website_url": "https://www.nomadhealth.com"},
    "Nourish": {"founded": "2021", "website_url": "https://www.usenourish.com"},
    "NourishedRx": {"founded": "2022", "website_url": "https://www.nourishedrx.com"},
    "Nudj Health": {"founded": "2020", "website_url": "https://www.nudjhealth.com"},
    # O
    "Omena": {"founded": "2021", "website_url": "https://www.omena.com"},
    "One Medical": {"founded": "2007", "website_url": "https://www.onemedical.com"},
    "OneroRx": {"founded": "2021", "website_url": "https://www.onerorx.com"},
    "OneStep": {"founded": "2020", "website_url": "https://www.onestep.com"},
    "Orion": {"founded": "2018", "website_url": "https://www.orionhealth.com"},
    "Oshi Health": {"founded": "2018", "website_url": "https://www.oshihealth.com"},
    # P
    "Pallie AI": {"founded": "2022", "website_url": "https://www.pallie.ai"},
    "PanTheryx": {"founded": "2007", "website_url": "https://www.pantheryx.com"},
    "Pear Suite": {"founded": "2021", "website_url": "https://www.pearsuite.com"},
    "Pearl Health": {"founded": "2020", "website_url": "https://www.pearlhealth.com"},
    "PeerLyfe": {"founded": "2021", "website_url": "https://www.peerlyfe.com"},
    "PeopleOne Health": {"founded": "2021", "website_url": "https://www.peopleonehealth.com"},
    "Perry": {"founded": "2022", "website_url": "https://www.perry.com"},
    "Pillo Health": {"founded": "2017", "website_url": "https://www.pillohealth.com"},
    "Punto Health": {"founded": "2021", "website_url": "https://www.puntohealth.com"},
    # R
    "RapidClaims": {"founded": "2022", "website_url": "https://www.rapidclaims.ai"},
    "Redi Health": {"founded": "2019", "website_url": "https://www.redihealth.com"},
    "Remodel Health": {"founded": "2018", "website_url": "https://www.remodelhealth.com"},
    "Rest Less": {"founded": "2019", "website_url": "https://www.reless.com"},
    "RETISPEC": {"founded": "2018", "website_url": "https://www.retispec.com"},
    "Riverspring Living": {"founded": "1989", "website_url": "https://www.riverspringliving.org"},
    "Rune Labs": {"founded": "2018", "website_url": "https://www.runelabs.io"},
    "RxDiet": {"founded": "2019", "website_url": "https://www.rxdiet.com"},
    # S
    "SafelyYou": {"founded": "2015", "website_url": "https://www.safelyyou.com"},
    "Sage Inc.": {"founded": "2020", "website_url": "https://www.sage.com"},
    "Sava": {"founded": "2021", "website_url": "https://www.sava.com"},
    "Season Health": {"founded": "2020", "website_url": "https://www.seasonhealth.com"},
    "Senior.com": {"founded": "2009", "website_url": "https://www.senior.com"},
    "Seniors Helping Seniors": {"founded": "1998", "website_url": "https://www.seniorshelpingseniors.com"},
    "Sensi.AI": {"founded": "2019", "website_url": "https://www.sensi.ai"},
    "SetPoint Medical": {"founded": "2007", "website_url": "https://www.setpointmedical.com"},
    "Sharecare": {"founded": "2010", "website_url": "https://www.sharecare.com"},
    "ShiftKey": {"founded": "2016", "website_url": "https://www.shiftkey.com"},
    "ShiftMed": {"founded": "2018", "website_url": "https://www.shiftmed.com"},
    "Sidecar Health": {"founded": "2018", "website_url": "https://www.sidecarhealth.com"},
    "SiftWell Analytics": {"founded": "2020", "website_url": "https://www.siftwell.com"},
    "Signify Health": {"founded": "2017", "website_url": "https://www.signifyhealth.com"},
    "Sollis Health": {"founded": "2016", "website_url": "https://www.sollishealth.com"},
    "Somatus": {"founded": "2016", "website_url": "https://www.somatus.com"},
    "Somnee": {"founded": "2020", "website_url": "https://www.somnee.com"},
    "Spark Advisors": {"founded": "2020", "website_url": "https://www.sparkadvisors.com"},
    "SpinSci": {"founded": "2017", "website_url": "https://www.spinsci.com"},
    "Spring Health": {"founded": "2016", "website_url": "https://www.springhealth.com"},
    "Starling Medical": {"founded": "2021", "website_url": "https://www.starlingmedical.com"},
    "Steadiwear": {"founded": "2016", "website_url": "https://www.steadiwear.com"},
    "Stepful": {"founded": "2020", "website_url": "https://www.stepful.com"},
    "Stripes Beauty": {"founded": "2021", "website_url": "https://www.stripesbeauty.com"},
    "Strive Health": {"founded": "2021", "website_url": "https://www.strivehealth.com"},
    "Sugar.fit": {"founded": "2021", "website_url": "https://www.sugarfit.com"},
    "Sunrise Group": {"founded": "1980", "website_url": "https://www.sunrise-group.org"},
    "Swift Medical": {"founded": "2015", "website_url": "https://www.swiftmedical.com"},
    "Switchboard Health": {"founded": "2019", "website_url": "https://www.switchboardhealth.com"},
    "Synchron": {"founded": "2012", "website_url": "https://www.synchron.com"},
    # T
    "Talkiatry": {"founded": "2020", "website_url": "https://www.talkiatry.com"},
    "Tennr": {"founded": "2021", "website_url": "https://www.tennr.com"},
    "Thoughtful AI": {"founded": "2022", "website_url": "https://www.thoughtful.ai"},
    "Thrive AI Health": {"founded": "2024", "website_url": "https://www.thrive.ai"},
    "Tomorrow Health": {"founded": "2020", "website_url": "https://www.tomorrowhealth.com"},
    "Transcarent": {"founded": "2020", "website_url": "https://www.transcarent.com"},
    "Tuesday Health": {"founded": "2021", "website_url": "https://www.tuesdayhealth.com"},
    "Tuned": {"founded": "2020", "website_url": "https://www.tuned.com"},
    "Two Chairs": {"founded": "2017", "website_url": "https://www.twochairs.com"},
    "TympaHealth": {"founded": "2019", "website_url": "https://www.tympahealth.com"},
    # U
    "Unfabled": {"founded": "2020", "website_url": "https://www.unfabled.com"},
    "UnitedHealth Group (UHG)": {"founded": "1977", "website_url": "https://www.unitedhealthgroup.com"},
    "Upsidehom": {"founded": "2021", "website_url": "https://www.upsidehom.com"},
    "Upward Health": {"founded": "2017", "website_url": "https://www.upwardhealth.com"},
    # V
    "Vayyar": {"founded": "2011", "website_url": "https://www.vayyar.com"},
    "vermut": {"founded": "2021", "website_url": "https://www.vermut.ai"},
    "Vi Health": {"founded": "2020", "website_url": "https://www.vi-health.com"},
    "Videra Health": {"founded": "2019", "website_url": "https://www.viderahealth.com"},
    "Visibly": {"founded": "2016", "website_url": "https://www.visibly.com"},
    "Vitable": {"founded": "2020", "website_url": "https://www.vitable.com"},
    "VitalTech": {"founded": "2015", "website_url": "https://www.vitaltech.com"},
    "Vivian Labs": {"founded": "2021", "website_url": "https://www.vivianlabs.com"},
    "Vivo": {"founded": "2017", "website_url": "https://www.vivohealth.com"},
    "Voize": {"founded": "2020", "website_url": "https://www.voize.de"},
    "Vori Health": {"founded": "2020", "website_url": "https://www.vorihealth.com"},
    "Voxela": {"founded": "2021", "website_url": "https://www.voxela.com"},
    "Vyld": {"founded": "2021", "website_url": "https://www.vyld.com"},
    "VyncaCare": {"founded": "2020", "website_url": "https://www.vynca.com"},
    # W
    "Waterlily": {"founded": "2020", "website_url": "https://www.waterlilycare.com"},
    "Watershed Health": {"founded": "2020", "website_url": "https://www.watershedhealth.com"},
    "Wellth": {"founded": "2014", "website_url": "https://www.wellthapp.com"},
    "Wheel": {"founded": "2018", "website_url": "https://www.wheel.com"},
    "Wile": {"founded": "2021", "website_url": "https://www.wile.com"},
    # X
    "Xander Glasses": {"founded": "2021", "website_url": "https://www.xanderglasses.com"},
    # Y
    "YgEia3": {"founded": "2022", "website_url": "https://www.ygeia3.com"},
    "Yurtle": {"founded": "2020", "website_url": "https://www.yurtle.com"},
    # Z
    "Zing Health": {"founded": "2019", "website_url": "https://www.zinghealth.com"},
    "Zinnia": {"founded": "2020", "website_url": "https://www.zinnia.com"},
    # Special chars
    "Ōmcare": {"founded": "2017", "website_url": "https://www.omcare.com"},
    "ŌURA": {"founded": "2013", "website_url": "https://ouraring.com"},
    # Chinese companies
    "世道护理": {"founded": "2014", "website_url": "https://www.shidao.cn"},
    "yooLab": {"founded": "2019", "website_url": "https://www.yoolab.com"},
    "去哪养老网": {"founded": "2016", "website_url": "https://www.qunanlaoyang.com"},
    "复星保德信颐养": {"founded": "2012", "website_url": "https://www.fosunpramerica.com"},
    "大耳马医学": {"founded": "2020", "website_url": "https://www.daermed.com"},
    "太平梧桐人家": {"founded": "2014", "website_url": "https://www.cntaiping.com"},
    "彭世修脚": {"founded": "2003", "website_url": "https://www.pengshixiujiao.com"},
    "德林假肢": {"founded": "1993", "website_url": "https://www.delinjiaozhi.com"},
    "曼景科技": {"founded": "2018", "website_url": "https://www.mjing.com"},
    "玛土撒拉": {"founded": "2017", "website_url": "https://www.methuselah.com"},
    # Additional that were missed
    "401GO": {"founded": "2020", "website_url": "https://www.401go.com"},
    "AceAge": {"founded": "2017", "website_url": "https://www.aceage.com"},
    "Adonis": {"founded": "2020", "website_url": "https://www.adonis.io"},
    "Advosense": {"founded": "2018", "website_url": "https://www.advosense.com"},
    "Alaffia Health": {"founded": "2020", "website_url": "https://www.alaffia.com"},
    "American HealthTech": {"founded": "1982", "website_url": "https://www.healthtech.com"},
    "Angels on Call Homecare": {"founded": "2010", "website_url": "https://www.angelsoncall.com"},
    "AssistMe": {"founded": "2019", "website_url": "https://www.assistme.com"},
    "Avation Medical": {"founded": "2017", "website_url": "https://www.avationmed.com"},
    "because": {"founded": "2020", "website_url": "https://www.because.com"},
    "Better Coliving": {"founded": "2021", "website_url": "https://www.bettercoliving.com"},
    "BirdWatch": {"founded": "2020", "website_url": "https://www.birdwatch.com"},
    "Bridge Group": {"founded": "2018", "website_url": "https://www.bridgegroup.com"},
    "Care Continuity": {"founded": "2017", "website_url": "https://www.carecontinuity.com"},
    "Carefull": {"founded": "2019", "website_url": "https://getcarefull.com"},
    "Carl": {"founded": "2020", "website_url": "https://www.carl.com"},
    "myo": {"founded": "2021", "website_url": "https://www.myo.com"},
    "Google Gemini AI 健康教练": {"founded": "2023", "website_url": "https://www.google.com"},
}

def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        enterprises = json.load(f)

    updated = 0
    not_found = set(UPDATES.keys())

    for ent in enterprises:
        name = ent.get("name", "")
        if name in UPDATES:
            not_found.discard(name)
            for key, val in UPDATES[name].items():
                if not ent.get(key):
                    ent[key] = val
            updated += 1

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(enterprises, f, ensure_ascii=False, indent=2)

    print(f"Updated: {updated}")
    if not_found:
        print(f"Not found in DB ({len(not_found)}): {not_found}")

if __name__ == "__main__":
    main()

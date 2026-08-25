from escpos.printer import Usb
import usb

# Initialize the thermal printer
p = Usb(idVendor=0x28e9, idProduct=0x0289, in_ep=0x81, out_ep=0x03, width=384)
lipsum = """ Erat autem homo ex Pharisaeis, Nicodemus nomine, princeps Iudaeorum. 2 Hic venit ad eum nocte et dixit ei: "Rabbi, scimus quia a Deo venisti magister. Nemo enim potest haec signa facere quae tu facis nisi fuerit Deus cum eo." 3 Respondit Iesus et dixit ei: "Amen, amen dico tibi: nisi quis natus fuerit denuo non potest videre regnum Dei". 4 Dicit ad eum Nicodemus: "Quomodo potest homo nasci cum senex sit? Numquid potest in ventrem matris suae iterato introire et nasci?" 5 Respondit Iesus: "Amen, amen dico tibi: nisi quis renatus fuerit ex aqua et Spiritu non potest introire in regnum Dei. 6 Quod natum est ex carne caro est et quod natum est ex Spiritu spiritus est. 7 Non mireris quia dixi tibi oportet vos nasci denuo. 8 Spiritus ubi vult spirat et vocem eius audis sed non scis unde veniat et quo vadat; sic est omnis qui natus est ex Spiritu." 9 Respondit Nicodemus et dixit ei: "Quomodo possunt haec fieri?" 10 Respondit Iesus et dixit ei: "Tu es magister Israhel et haec ignoras? 11 Amen, amen dico tibi quia quod scimus loquimur et quod vidimus testamur et testimonium nostrum non accipitis. 12 Si terrena dixi vobis et non creditis quomodo si dixero vobis caelestia credetis? 13 Et nemo ascendit in caelum nisi qui descendit de caelo, Filius hominis qui est in caelo. 14 Et sicut Moses exaltavit serpentem in deserto, ita exaltari oportet Filium hominis 15 ut omnis qui credit in ipso non pereat sed habeat vitam aeternam. 16 Sic enim dilexit Deus mundum ut Filium suum unigenitum daret ut omnis qui credit in eum non pereat sed habeat vitam aeternam. 17 Non enim misit Deus Filium suum in mundum ut iudicet mundum sed ut salvetur mundus per ipsum. 18 Qui credit in eum non iudicatur; qui autem non credit iam iudicatus est, quia non credidit in nomine unigeniti Filii Dei. 19 Hoc est autem iudicium quia lux venit in mundum et dilexerunt homines magis tenebras quam lucem; erant enim eorum mala opera. 20 Omnis enim qui mala agit odit lucem et non venit ad lucem ut non arguantur opera eius; 21 qui autem facit veritatem venit ad lucem ut manifestentur eius opera quia in Deo sunt facta."

22 Post haec venit Iesus et discipuli eius in Iudaeam terram et illic demorabatur cum eis et baptizabat. 23 Erat autem et Iohannes baptizans in Aenon iuxta Salim quia aquae multae erant illic et adveniebant et baptizabantur; 24 nondum enim missus fuerat in carcerem Iohannes.

25 Facta est ergo quaestio ex discipulis Iohannis cum Iudaeis de purificatione. 26 Et venerunt ad Iohannem et dixerunt ei: "Rabbi, qui erat tecum trans Iordanen cui tu testimonium perhibuisti, ecce hic baptizat et omnes veniunt ad eum." 27 Respondit Iohannes et dixit: "Non potest homo accipere quicquam nisi fuerit ei datum de caelo. 28 Ipsi vos mihi testimonium perhibetis quod dixerim: ego non sum Christus sed quia missus sum ante illum. 29 Qui habet sponsam sponsus est; amicus autem sponsi, qui stat et audit eum, gaudio gaudet propter vocem sponsi. Hoc ergo gaudium meum impletum est. 30 Illum oportet crescere, me autem minui."

31 Qui desursum venit supra omnes est; qui est de terra de terra est et de terra loquitur. Qui de caelo venit supra omnes est; 32 et quod vidit et audivit hoc testatur et testimonium eius nemo accipit. 33 Qui accipit eius testimonium signavit quia Deus verax est. 34 Quem enim misit Deus, verba Dei loquitur, non enim ad mensuram dat Deus Spiritum. 35 Pater diligit Filium et omnia dedit in manu eius. 36 Qui credit in Filium habet vitam aeternam; qui autem incredulus est Filio, non videbit vitam sed ira Dei manet super eum. """


small = """\n\n\n\n\n\n\n\n"""

while True:
    try:
        p.text(lipsum)

    except usb.core.USBError as e:
        print(f"USB error: {e}")
        print("Printer connection lost. Stopping.")
        break

    except Exception as e:
        print(f"Unexpected error: {e}")
        break
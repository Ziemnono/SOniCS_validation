# SOniCS_validation
<h2>SOFA, FEniCSx, and FEBio codes for SOniCS paper</h2>
 
In this work, we describe the SOniCS (SOFA + FEniCS) plugin to help develop intuitive understanding of complex biomechanics systems. This new approach allows the user to experiment with model choices easily and quickly without requiring in-depth expertise. Constitutive models can be modified by one line of code only. This ease in building new models makes SOniCS ideal to develop surrogate, reduced order models and to train machine learning algorithms for enabling real-time patient-specific simulations. SOniCS is thus not only a tool that facilitates the development of surgical training simulations but also, and perhaps more importantly, paves the way to increase the intuition of users or otherwise non-intuitive behaviors of (bio)mechanical systems. The plugin uses new developments of the FEniCSx project enabling automatic generation with FFCx of finite element tensors such as the local residual vector and Jacobian matrix. We verify our approach with numerical simulations such as manufactured solutions, cantilever beams, and benchmarks provided by FEBio. We reach machine precision accuracy and demonstrate the use of the plugin for a real-time haptic simulation involving a surgical tool controlled by the user in contact with a hyperelastic liver. We include complete examples showing the use of our plugin for simulations involving Saint Venant-Kirchhoff, Neo-Hookean, Mooney-Rivlin, and Holzapfel Ogden anisotropic models as supplementary material.

<h2>FEniCSx</h2>
This paper relies on new development of the FEniCS project called FEniCSx, more information can be found on the GitHub repository: https://github.com/FEniCS or the website https://fenicsproject.org/

The easiest way is to run Docker using 
```console
docker run -ti -v $(pwd):/root/shared dolfinx/dolfinx:latest
```

<h2>SOFA</h2>
We also used SOFA for comparing our SOniCS simulations.
To download SOFA: https://www.sofa-framework.org/download/ and know more about it: https://www.sofa-framework.org/.

<h2>SOniCS</h2>
The SOniCS plugin has be developed as an extra feature of the Caribou plugin. To install it, pelease follow the installation steps https://github.com/mimesis-inria/caribou/tree/FeniCS-features. Only the build option is available for the moment.

<h2>Optional</h2>
<h3>FEBio</h3>
We also used FEBio for comparing our SOniCS simulations. To download FEBio: https://febio.org/downloads/

<h3>SOFA Geomagic plugin</h3>
To use an haptic device, we used the SOFA Geomagic plugin. Installation steps can be found on the Github repository: https://github.com/sofa-framework/sofa/tree/master/applications/plugins/Geomagic


<h2>Strcture of the repository</h2>
The directory contains the different examples used in the paper. They have been implemented using SOFA, FeniCSx, and FEBio:

* fenics_manufactured_solution.py: beam manufactured solution example. The variables order can be set to "quadratic" or "linear", element could be "tetrahedron" or "hexahedron", and material "SaintVenantKirchhoff" or "NeoHookean". 
* beam_convergence.py and fenics_beam_HO_convergence.py: beam convergence study of the HO anisotropic material using SOniCS and FEniCSx respectively.
* fenics_liver_HO_convergence.py: liver convergence study of the HO anisotropic material using FEniCSx implementation.
* haptic.py: liver haptic simulation in contact with a surgical tool. Can only be ran using the SOFA Geomagic plugin and a compatible haptic device.
* convergence_study: directory containing all the files used for the convergence study of the beam and liver meshes.
* febio validation: directory comparing the FEBio and SOniCS implementation. The file febio_rectangular_beam_bending_static_stvk.py is running the simulation while the parameters.py can tune the parameters of the scene (e.g., material model, force intensity, mesh, etc..).Can only be ran if FEBio is installed
* manufactured_solution: directory containing necessary methods defined for the manufactured solutions.
* meshes: directory containing the meshes used in the study.

## Running the code
To simply run the codes:
```
python3 file_name.py
```

FEniCSx also offers parallel computation:
```
mpirun -n N python3 file_name.py
```
where N is the number of core you want to use.

## Full paper
https://arxiv.org/abs/2208.11676

## Information
### Authors 
- Arnaud Mazier: Department of Computational Science, Université du Luxembourg, Esch-sur-Alzette, Luxembourg
- Sidaty El Hadramy: MIMESIS Team, Inria, 1 Place de l'Hôpital, Strasbourg, France
- Jean-Nicolas Brunet: MIMESIS Team, Inria, 1 Place de l'Hôpital, Strasbourg, France
- Jack S. Hale: Department of Computational Science, Université du Luxembourg, Esch-sur-Alzette, Luxembourg
- Stéphane Cotin: MIMESIS Team, Inria, 1 Place de l'Hôpital, Strasbourg, France
- Stéphane P.A. Bordas: Department of Computational Science, Université du Luxembourg, Esch-sur-Alzette, Luxembourg

### Contact 
mazier.arnaud@gmail.com and sidaty.el-hadramy@inria.fr or use the [Discussion feature from Github](https://github.com/Ziemnono/SOniCS_validation/discussions)
